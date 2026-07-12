import { useEffect, useState } from "react";
import { getVehicles, createMaintenance, closeMaintenance } from "../api/api";
import StatusBadge from "../components/StatusBadge";

export default function Maintenance() {
  const [vehicles, setVehicles] = useState([]);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({ vehicle_id: "", description: "", cost: "", date: "" });
  const [error, setError] = useState("");

  const load = async () => {
    const res = await getVehicles();
    setVehicles(res.data);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await createMaintenance(form);
      setLogs([...logs, res.data]);
      setForm({ vehicle_id: "", description: "", cost: "", date: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create maintenance record");
    }
  };

  const close = async (id) => {
    try {
      await closeMaintenance(id);
      setLogs(logs.filter(l => l.id !== id));
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to close maintenance");
    }
  };

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
        {vehicles.filter(v => v.status === "In Shop").map(v => (
          <div key={v.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
            <span className="font-medium">{v.registration_number}</span>
            <div className="flex items-center gap-2">
              <StatusBadge status={v.status} />
              <button onClick={() => close(v.maintenance_id || v.id)} className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                Close Maintenance
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}