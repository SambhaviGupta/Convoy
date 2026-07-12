import { useEffect, useState } from "react";
import { getVehicles, createVehicle, getErrorMessage } from "../api/api";
import StatusBadge from "../components/StatusBadge";

export default function Vehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [form, setForm] = useState({
    registration_number: "", name_model: "", type: "",
    max_load_capacity: "", odometer: "", acquisition_cost: ""
  });
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
    const payload = {
      ...form,
      max_load_capacity: form.max_load_capacity === "" ? null : Number(form.max_load_capacity),
      odometer: form.odometer === "" ? null : Number(form.odometer),
      acquisition_cost: form.acquisition_cost === "" ? null : Number(form.acquisition_cost),
    };
    await createVehicle(payload);
    setForm({ registration_number: "", name_model: "", type: "", max_load_capacity: "", odometer: "", acquisition_cost: "" });
    load();
  } catch (err) {
    const detail = err.response?.data?.detail;
    let message = "Failed to add vehicle";
    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail.map(d => `${d.loc?.[d.loc.length - 1]}: ${d.msg}`).join(", ");
    }
    setError(message);
  }
};

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Vehicles</h1>

      <form onSubmit={submit} className="grid grid-cols-3 gap-3 mb-6 bg-white p-4 rounded-lg shadow">
        <input placeholder="Registration Number" value={form.registration_number}
          onChange={e => setForm({ ...form, registration_number: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="Name/Model" value={form.name_model}
          onChange={e => setForm({ ...form, name_model: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="Type" value={form.type}
          onChange={e => setForm({ ...form, type: e.target.value })}
          className="border p-2 rounded" required />
        <input type="number" placeholder="Max Load Capacity (kg)" value={form.max_load_capacity}
          onChange={e => setForm({ ...form, max_load_capacity: e.target.value })}
          className="border p-2 rounded" required />
        <input type="number" placeholder="Odometer" value={form.odometer}
          onChange={e => setForm({ ...form, odometer: e.target.value })}
          className="border p-2 rounded" />
        <input type="number" placeholder="Acquisition Cost" value={form.acquisition_cost}
          onChange={e => setForm({ ...form, acquisition_cost: e.target.value })}
          className="border p-2 rounded" />
        <button className="col-span-3 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Add Vehicle
        </button>
        {error && <p className="col-span-3 text-red-600 text-sm">{error}</p>}
      </form>

      <div className="space-y-2">
        {vehicles.map(v => (
          <div key={v.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
            <div>
              <span className="font-medium">{v.registration_number}</span>
              <span className="ml-3 text-sm text-gray-500">{v.name_model} · {v.type} · {v.max_load_capacity}kg</span>
            </div>
            <StatusBadge status={v.status} />
          </div>
        ))}
      </div>
    </div>
  );
}