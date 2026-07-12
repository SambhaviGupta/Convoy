import { useEffect, useState } from "react";
import { getVehicles, getMaintenance, createMaintenance, closeMaintenance, getErrorMessage } from "../api/api";
import StatusBadge from "../components/StatusBadge";

export default function Maintenance() {
  const [vehicles, setVehicles] = useState([]);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({ vehicle_id: "", description: "", cost: "", date: "" });
  const [error, setError] = useState("");

  const load = async () => {
    const [vehiclesRes, logsRes] = await Promise.all([getVehicles(), getMaintenance()]);
    setVehicles(vehiclesRes.data);
    setLogs(logsRes.data);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createMaintenance(form);
      setForm({ vehicle_id: "", description: "", cost: "", date: "" });
      load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create maintenance record"));
    }
  };

  const close = async (maintenanceId) => {
    try {
      await closeMaintenance(maintenanceId);
      load();
    } catch (err) {
      alert(getErrorMessage(err, "Failed to close maintenance"));
    }
  };

  // Active maintenance logs, joined with their vehicle's registration number,
  // so "Close Maintenance" always operates on the real MaintenanceLog.id
  // rather than guessing/reusing the vehicle's id.
  const activeLogs = logs
    .filter(l => l.is_active)
    .map(l => ({
      ...l,
      vehicle: vehicles.find(v => v.id === l.vehicle_id),
    }));

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Maintenance</h1>

      <form onSubmit={submit} className="grid grid-cols-2 gap-3 mb-6 bg-white p-4 rounded-lg shadow">
        <select value={form.vehicle_id}
          onChange={e => setForm({ ...form, vehicle_id: e.target.value })}
          className="border p-2 rounded" required>
          <option value="">Select Vehicle</option>
          {vehicles.map(v => (
            <option key={v.id} value={v.id}>{v.registration_number}</option>
          ))}
        </select>
        <input placeholder="Description (e.g. Oil Change)" value={form.description}
          onChange={e => setForm({ ...form, description: e.target.value })}
          className="border p-2 rounded" required />
        <input type="number" placeholder="Cost" value={form.cost}
          onChange={e => setForm({ ...form, cost: e.target.value })}
          className="border p-2 rounded" required />
        <input type="date" value={form.date}
          onChange={e => setForm({ ...form, date: e.target.value })}
          className="border p-2 rounded" required />
        <button className="col-span-2 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Create Maintenance Record
        </button>
        {error && <p className="col-span-2 text-red-600 text-sm">{error}</p>}
      </form>

      <div className="space-y-2">
        {activeLogs.map(log => (
          <div key={log.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
            <span className="font-medium">
              {log.vehicle?.registration_number || `Vehicle #${log.vehicle_id}`}
              <span className="text-gray-400 text-sm ml-2">{log.description}</span>
            </span>
            <div className="flex items-center gap-2">
              {log.vehicle && <StatusBadge status={log.vehicle.status} />}
              <button onClick={() => close(log.id)} className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                Close Maintenance
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
