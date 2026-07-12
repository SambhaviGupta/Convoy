import { useEffect, useState } from "react";
import { getDrivers, createDriver } from "../api/api";
import StatusBadge from "../components/StatusBadge";

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [form, setForm] = useState({
    name: "", license_number: "", license_category: "",
    license_expiry_date: "", contact_number: ""
  });
  const [error, setError] = useState("");

  const load = async () => {
    const res = await getDrivers();
    setDrivers(res.data);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createDriver(form);
      setForm({ name: "", license_number: "", license_category: "", license_expiry_date: "", contact_number: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add driver");
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Drivers</h1>

      <form onSubmit={submit} className="grid grid-cols-3 gap-3 mb-6 bg-white p-4 rounded-lg shadow">
        <input placeholder="Name" value={form.name}
          onChange={e => setForm({ ...form, name: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="License Number" value={form.license_number}
          onChange={e => setForm({ ...form, license_number: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="License Category" value={form.license_category}
          onChange={e => setForm({ ...form, license_category: e.target.value })}
          className="border p-2 rounded" required />
        <input type="date" placeholder="License Expiry Date" value={form.license_expiry_date}
          onChange={e => setForm({ ...form, license_expiry_date: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="Contact Number" value={form.contact_number}
          onChange={e => setForm({ ...form, contact_number: e.target.value })}
          className="border p-2 rounded" />
        <button className="col-span-3 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Add Driver
        </button>
        {error && <p className="col-span-3 text-red-600 text-sm">{error}</p>}
      </form>

      <div className="space-y-2">
        {drivers.map(d => (
          <div key={d.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
            <div>
              <span className="font-medium">{d.name}</span>
              <span className="ml-3 text-sm text-gray-500">{d.license_number} · Expires {d.license_expiry_date}</span>
            </div>
            <StatusBadge status={d.status} />
          </div>
        ))}
      </div>
    </div>
  );
}