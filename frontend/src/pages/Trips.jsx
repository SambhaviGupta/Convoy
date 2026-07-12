import { useEffect, useState } from "react";
import { getTrips, createTrip, dispatchTrip, completeTrip, cancelTrip, getAvailableVehicles, getAvailableDrivers, getErrorMessage } from "../api/api";
import StatusBadge from "../components/StatusBadge";

export default function Trips() {
  const [trips, setTrips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [form, setForm] = useState({
    source: "", destination: "", vehicle_id: "", driver_id: "",
    cargo_weight: "", planned_distance: ""
  });
  const [error, setError] = useState("");

  const load = async () => {
    const [t, v, d] = await Promise.all([getTrips(), getAvailableVehicles(), getAvailableDrivers()]);
    setTrips(t.data);
    setVehicles(v.data);
    setDrivers(d.data);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createTrip(form);
      setForm({ source: "", destination: "", vehicle_id: "", driver_id: "", cargo_weight: "", planned_distance: "" });
      load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create trip"));
    }
  };

  const act = async (action, id) => {
    try {
      if (action === "dispatch") await dispatchTrip(id);
      if (action === "complete") await completeTrip(id, { actual_odometer_end: 0, fuel_consumed: 0 });
      if (action === "cancel") await cancelTrip(id);
      load();
    } catch (err) {
      alert(getErrorMessage(err, "Action failed"));
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Trips</h1>

      <form onSubmit={submit} className="grid grid-cols-3 gap-3 mb-6 bg-white p-4 rounded-lg shadow">
        <input placeholder="Source" value={form.source}
          onChange={e => setForm({ ...form, source: e.target.value })}
          className="border p-2 rounded" required />
        <input placeholder="Destination" value={form.destination}
          onChange={e => setForm({ ...form, destination: e.target.value })}
          className="border p-2 rounded" required />
        <select value={form.vehicle_id}
          onChange={e => setForm({ ...form, vehicle_id: e.target.value })}
          className="border p-2 rounded" required>
          <option value="">Select Vehicle</option>
          {vehicles.map(v => (
            <option key={v.id} value={v.id}>{v.registration_number} ({v.max_load_capacity}kg)</option>
          ))}
        </select>
        <select value={form.driver_id}
          onChange={e => setForm({ ...form, driver_id: e.target.value })}
          className="border p-2 rounded" required>
          <option value="">Select Driver</option>
          {drivers.map(d => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
        <input type="number" placeholder="Cargo Weight (kg)" value={form.cargo_weight}
          onChange={e => setForm({ ...form, cargo_weight: e.target.value })}
          className="border p-2 rounded" required />
        <input type="number" placeholder="Planned Distance (km)" value={form.planned_distance}
          onChange={e => setForm({ ...form, planned_distance: e.target.value })}
          className="border p-2 rounded" required />
        <button className="col-span-3 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Create Trip
        </button>
        {error && <p className="col-span-3 text-red-600 text-sm">{error}</p>}
      </form>

      <div className="space-y-2">
        {trips.map(t => (
          <div key={t.id} className="flex justify-between items-center bg-white p-3 rounded shadow">
            <div>
              <span className="font-medium">{t.source} → {t.destination}</span>
              <span className="ml-3 text-sm text-gray-500">{t.cargo_weight}kg</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={t.status} />
              {t.status === "Draft" && (
                <button onClick={() => act("dispatch", t.id)} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                  Dispatch
                </button>
              )}
              {t.status === "Dispatched" && (
                <>
                  <button onClick={() => act("complete", t.id)} className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                    Complete
                  </button>
                  <button onClick={() => act("cancel", t.id)} className="text-xs bg-red-600 text-white px-2 py-1 rounded">
                    Cancel
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}