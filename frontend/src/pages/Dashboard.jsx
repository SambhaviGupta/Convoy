import { useEffect, useState } from "react";
import { getKpis } from "../api/api";

export default function Dashboard() {
  const [kpis, setKpis] = useState({});

  useEffect(() => {
    getKpis().then(r => setKpis(r.data)).catch(() => {});
  }, []);

  const cards = [
    ["Active Vehicles", kpis.active_vehicles],
    ["Available Vehicles", kpis.available_vehicles],
    ["In Maintenance", kpis.vehicles_in_maintenance],
    ["Active Trips", kpis.active_trips],
    ["Pending Trips", kpis.pending_trips],
    ["Drivers On Duty", kpis.drivers_on_duty],
    ["Fleet Utilization", `${kpis.fleet_utilization_percent ?? 0}%`],
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-4 gap-4">
        {cards.map(([label, value]) => (
          <div key={label} className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-500 text-sm">{label}</p>
            <p className="text-2xl font-bold">{value ?? "—"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}