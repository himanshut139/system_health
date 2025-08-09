<template>
  <div>
    <h1>Admin Dashboard - Machines Health</h1>

    <div>
      <label>Filter by OS:</label>
      <input v-model="osFilter" placeholder="e.g. Windows" @keyup.enter="fetchMachines" />
      <label>Filter by Issues (comma separated):</label>
      <input v-model="issuesFilter" placeholder="e.g. disk_encryption,sleep_ok" @keyup.enter="fetchMachines" />
      <button @click="fetchMachines">Apply Filters</button>
      <button @click="resetFilters">Reset</button>
    </div>

    <table border="1" cellpadding="8" cellspacing="0" style="margin-top: 1em;">
      <thead>
        <tr>
          <th>Machine ID</th>
          <th>OS</th>
          <th>Last Check</th>
          <th>Disk Encryption</th>
          <th>OS Up to Date</th>
          <th>Antivirus</th>
          <th>Sleep OK</th>
        </tr>
      </thead>
      <tbody>
  <tr v-if="machines.length === 0">
    <td colspan="7" style="text-align:center;">No machines found.</td>
  </tr>
  <tr v-for="machine in machines" :key="machine.machine_id">
    <td>{{ machine.machine_id }}</td>
    <td>{{ machine.os }}</td>
    <td>{{ machine.last_check }}</td>

    <td
      :style="{ color: machine.latest_report.disk_encryption ? 'green' : 'red' }"
      :title="machine.latest_report.disk_encryption
        ? 'Disk is encrypted and secure'
        : 'Disk is NOT encrypted, risk of data loss'"
    >
      {{ machine.latest_report.disk_encryption ? 'Secure' : 'Not Secure' }}
    </td>

    <td
      :style="{ color: machine.latest_report.os_up_to_date ? 'green' : 'red' }"
      :title="machine.latest_report.os_up_to_date
        ? 'Operating system is up to date'
        : 'Operating system update is pending'"
    >
      {{ machine.latest_report.os_up_to_date ? 'Up to Date' : 'Update Needed' }}
    </td>

    <td
      :style="{ color: machine.latest_report.antivirus ? 'green' : 'red' }"
      :title="machine.latest_report.antivirus
        ? 'Antivirus is active'
        : 'Antivirus is missing or inactive'"
    >
      {{ machine.latest_report.antivirus ? 'Active' : 'Inactive' }}
    </td>

    <td
      :style="{ color: machine.latest_report.sleep_ok ? 'green' : 'red' }"
      :title="machine.latest_report.sleep_ok
        ? 'Sleep setting is 10 minutes or less'
        : 'Sleep setting is longer than 10 minutes'"
    >
      {{ machine.latest_report.sleep_ok ? 'OK' : 'Needs Attention' }}
    </td>
  </tr>
</tbody>

    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      machines: [],
      osFilter: '',
      issuesFilter: ''
    };
  },
  methods: {
    async fetchMachines() {
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
      let url = `${baseURL}/api/machines`;
      const params = new URLSearchParams();
      if(this.osFilter) params.append('os', this.osFilter);
      if(this.issuesFilter) params.append('issues', this.issuesFilter);
      if(params.toString()) url += `?${params.toString()}`;

      try {
        const res = await fetch(url);
        if(!res.ok) throw new Error('Failed to fetch data');
        this.machines = await res.json();
      } catch (err) {
        alert('Error loading machines: ' + err.message);
      }
    },
    resetFilters() {
      this.osFilter = '';
      this.issuesFilter = '';
      this.fetchMachines();
    }
  },
  mounted() {
    this.fetchMachines();
  }
}
</script>

<style>

</style>
