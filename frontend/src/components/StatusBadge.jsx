const COLORS = {
  Available: "bg-green-100 text-green-700",
  "On Trip": "bg-blue-100 text-blue-700",
  "In Shop": "bg-orange-100 text-orange-700",
  Retired: "bg-gray-100 text-gray-600",
  "Off Duty": "bg-gray-100 text-gray-600",
  Suspended: "bg-red-100 text-red-700",
  Draft: "bg-gray-100 text-gray-600",
  Dispatched: "bg-blue-100 text-blue-700",
  Completed: "bg-green-100 text-green-700",
  Cancelled: "bg-red-100 text-red-700",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${COLORS[status] || "bg-gray-100"}`}>
      {status}
    </span>
  );
}