import os, json, csv, io
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

basedir=os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB="sqlite:///"+os.path.join(basedir,"data.db")
DB_URL=os.environ.get("DATABASE_URL", DEFAULT_DB)
API_KEY=os.environ.get("API_KEY","api12345")


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
CORS(app)
db=SQLAlchemy(app)


#_________Models

class Machine(db.Model):
    __tablename__="machine"
    id=db.Column(db.Integer, primary_key=True)
    machine_id=db.Column(db.String(128), unique=True, nullable=False, index=True)
    os=db.Column(db.String(64))
    last_check=db.Column(db.DateTime)

class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    machine_id=db.Column(db.String(128), db.ForeignKey("machine.machine_id"), nullable=False, index=True)
    timestamp=db.Column(db.DateTime, default=datetime.utcnow, index=True)
    disk_encryption=db.Column(db.Boolean)
    os_up_to_date=db.Column(db.Boolean)
    antivirus=db.Column(db.Boolean)
    sleep_ok=db.Column(db.Boolean)
    raw=db.Column(db.Text)


def require_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key=request.headers.get("X-API-KEY") or request.args.get("api_key")
        if key!=API_KEY:
            return jsonify({"error":"unauthorized"}), 401
        return f(*args,**kwargs)
    return wrapper



#_------------------------Routes----------------------------------


@app.route("/api/report", methods=["POST"])
@require_api
def api_report():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error":"No JSON body"}), 400
    
    machine_id=data.get("machine") or request.remote_addr
    os_name=data.get("os") or ""
    disk_enc = bool(data.get("disk_encryption"))
    os_up = bool(data.get("os_up_to_date"))
    anti_vr = bool(data.get("antivirus"))
    sleep_ok = bool(data.get("sleep_ok"))

    raw = json.dumps(data)

    m=Machine.query.filter_by(machine_id=machine_id).first()
    if not m:
        m = Machine(machine_id=machine_id, os=os_name, last_check=datetime.utcnow())
        db.session.add(m)
    else:
        m.os=os_name
        m.last_check=datetime.utcnow()


    r=Report(machine_id=machine_id,
             disk_encryption=disk_enc,
              os_up_to_date=os_up,
              antivirus=anti_vr,
                sleep_ok=sleep_ok,
                raw=raw)
    db.session.add(r)
    db.session.commit()
    return jsonify({"status":"received"}), 201

@app.route("/api/machines", methods=["GET"])
def api_machines():
    os_filter = request.args.get("os", type=str)
    issues_filter = request.args.get("issues", type=str)

    machines_list = []
    query = Machine.query

    if os_filter:
        query = query.filter(Machine.os.ilike(f"%{os_filter}%"))

    all_machines = query.all()  

    for machine in all_machines:
        latest_report = (
            Report.query
            .filter_by(machine_id=machine.machine_id)
            .order_by(Report.timestamp.desc())
            .first()
        )

        if not latest_report:
            continue  

        raw_parsed = {}
        try:
            raw_parsed = json.loads(latest_report.raw)
        except Exception:
            pass

        latest_json = {
            "timestamp": latest_report.timestamp.isoformat(),
            "disk_encryption": latest_report.disk_encryption,
            "os_up_to_date": latest_report.os_up_to_date,
            "antivirus": latest_report.antivirus,
            "sleep_ok": latest_report.sleep_ok,
            "metrics": raw_parsed
        }

        if issues_filter:
            issues = [issue.strip() for issue in issues_filter.split(",")]
            # Checking if any issue flag is False (meaning issue exists)
            has_issue = any(
                getattr(latest_report, issue, True) == False
                for issue in issues
            )
            if not has_issue:
                continue  

        machines_list.append({
            "machine_id": machine.machine_id,
            "os": machine.os,
            "last_check": machine.last_check.isoformat() if machine.last_check else None,
            "latest_report": latest_json
        })

    return jsonify(machines_list), 200

@app.route("/api/export", methods=["GET"])
def api_export():
    machines=Machine.query.all()
    si=io.StringIO()
    writer=csv.writer(si)
    writer.writerow(["machine_id","os","last_check","disk_encryption","os_up_to_date","antivirus","sleep_ok"])
    for m in machines:
        latest=Report.query.filter_by(machine_id=m.machine_id).order_by(Report.timestamp.desc()).first()
        writer.writerow([
            m.machine_id,
            m.os,
            m.last_check.isoformat() if m.last_check else "",
            latest.disk_encryption if latest else "",
            latest.os_up_to_date if latest else "",
            latest.antivirus if latest else "",
            latest.sleep_ok if latest else ""
        ])
    output=si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=machines_export.csv"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok", "time": datetime.utcnow().isoformat()}), 200

@app.route("/dashboard")
def dashboard():
    machines = []
    all_machines = Machine.query.all()
    for machine in all_machines:
        latest_report = (
            Report.query
            .filter_by(machine_id=machine.machine_id)
            .order_by(Report.timestamp.desc())
            .first()
        )
        machines.append({
            "machine_id": machine.machine_id,
            "os": machine.os,
            "last_check": machine.last_check,
            "report": latest_report
        })
    return render_template("dashboard.html", machines=machines)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)