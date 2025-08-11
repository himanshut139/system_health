<template>
  <div>
    <button @click="toggleView" class="toggle-btn">
      {{ showAll ? "🏠 View Current Machine's Health" : "🔍 View All Machines" }}
    </button>

    <div v-if="showAll">
      <div class="filters">
        <input v-model="filters.os" placeholder="Filter by OS" @keyup.enter="fetchMachines"/>
        <select v-model="filters.issue" @keyup.enter="fetchMachines">
          <option value="">All Issues</option>
          <option value="disk_encryption">Disk Encryption</option>
          <option value="os_up_to_date">OS Update</option>
          <option value="antivirus">Antivirus</option>
          <option value="sleep_ok">Sleep Mode</option>
        </select>
        <button @click="fetchMachines">Apply Filters</button>
        <a
          :href="`${apiBase}/api/export`"
          class="download-btn"
          target="_blank"
          rel="noopener noreferrer"
        >
          Download CSV
        </a>
      </div>

      <table>
        <thead>
          <tr>
            <th @click="sortBy('machine_id')">Machine ID</th>
            <th @click="sortBy('os')">OS</th>
            <th @click="sortBy('last_check')">Last Check</th>
            <th>Disk Encrypted</th>
            <th>OS Up-to-date</th>
            <th>Antivirus</th>
            <th>Sleep OK</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="machine in sortedMachines"
            :key="machine.machine_id"
            :class="{ 'issue-row': hasIssue(machine) }"
          >
            <td>{{ machine.machine_id }}</td>
            <td>{{ machine.os }}</td>
            <td>{{ formatDate(machine.last_check) }}</td>
            <td>{{ yesNo(machine.latest_report.disk_encryption) }}</td>
            <td>{{ yesNo(machine.latest_report.os_up_to_date) }}</td>
            <td>{{ yesNo(machine.latest_report.antivirus) }}</td>
            <td>{{ yesNo(machine.latest_report.sleep_ok) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else>
      <div
        class="health-card"
        :class="{
          healthy: isHealthy(currentMachine),
          unhealthy: !isHealthy(currentMachine)
        }"
      >
        <h2>💻 Current Machine's Health</h2>
        <p><strong>Machine ID:</strong> {{ currentMachine.machine_id }}</p>
        <p><strong>OS:</strong> {{ currentMachine.os }}</p>
        <p><strong>Last Check:</strong> {{ formatDate(currentMachine.last_check) }}</p>

        <table class="metrics-table">
          <tr>
            <td>Disk Encryption</td>
            <td>{{ yesNo(currentMachine.latest_report.disk_encryption) }}</td>
          </tr>
          <tr>
            <td>OS Up-to-date</td>
            <td>{{ yesNo(currentMachine.latest_report.os_up_to_date) }}</td>
          </tr>
          <tr>
            <td>Antivirus</td>
            <td>{{ yesNo(currentMachine.latest_report.antivirus) }}</td>
          </tr>
          <tr>
            <td>Sleep OK</td>
            <td>{{ yesNo(currentMachine.latest_report.sleep_ok) }}</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      machines: [],
      currentMachine: {
        machine_id: "unknown",
        os: "unknown",
        last_check: null,
        latest_report: {}
      },
      filters: { os: "", issue: "" },
      sortKey: "",
      sortOrder: 1,
      apiBase: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000",
      showAll: true
    };
  },
  computed: {
    sortedMachines() {
      let arr = [...this.machines];
      if (this.sortKey) {
        arr.sort((a, b) => {
          let valA = a[this.sortKey] || "";
          let valB = b[this.sortKey] || "";
          if (valA < valB) return -1 * this.sortOrder;
          if (valA > valB) return 1 * this.sortOrder;
          return 0;
        });
      }
      return arr;
    }
  },
  methods: {
    async fetchMachines() {
      try {
        let url = `${this.apiBase}/api/machines`;
        const params = [];
        if (this.filters.os) params.push(`os=${this.filters.os}`);
        if (this.filters.issue) params.push(`issues=${this.filters.issue}`);
        if (params.length) url += "?" + params.join("&");

        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch machines");
        this.machines = await res.json();

        if (this.machines.length) {
          this.currentMachine = this.machines[0];
        }
      } catch (err) {
        console.error(err);
      }
    },
    yesNo(value) {
      return value ? "✅" : "❌";
    },
    hasIssue(machine) {
      return !this.isHealthy(machine);
    },
    isHealthy(machine) {
      if (!machine || !machine.latest_report) return false;
      return (
        machine.latest_report.disk_encryption &&
        machine.latest_report.os_up_to_date &&
        machine.latest_report.antivirus &&
        machine.latest_report.sleep_ok
      );
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortOrder *= -1;
      } else {
        this.sortKey = key;
        this.sortOrder = 1;
      }
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleString() : "-";
    },
    toggleView() {
      this.showAll = !this.showAll;
    }
  },
  mounted() {
    this.fetchMachines();
  }
};
</script>

<style scoped>
.toggle-btn {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  background: #0077cc;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.toggle-btn:hover {
  background: #005fa3;
}
.filters {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th {
  cursor: pointer;
  background: #eee;
}
th,
td {
  border: 1px solid #ddd;
  padding: 0.5rem;
}
.issue-row {
  background-color: #fff8e1;
}
.download-btn {
  background: #4caf50;
  color: white;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 4px;
}
.health-card {
  padding: 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
  color: #333;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  background: #f9f9f9;
}
.health-card.healthy {
  border-left: 6px solid #4caf50;
}
.health-card.unhealthy {
  border-left: 6px solid #ff9800;
}
.metrics-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.metrics-table td {
  border: 1px solid #ddd;
  padding: 0.4rem 0.6rem;
}
.metrics-table td:first-child {
  font-weight: bold;
}
.filters {
  display: flex;
  justify-content: center; 
  align-items: center;     
  gap: 10px;            
  margin: 20px auto;  
  flex-wrap: wrap;     
}
.toggle-btn {
  margin-left: auto;    
  display: block;
}
</style>
