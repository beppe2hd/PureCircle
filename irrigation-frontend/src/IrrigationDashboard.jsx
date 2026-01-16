import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function IrrigationDashboard() {
  /* ---------------- STATE ---------------- */
  const [fields, setFields] = useState([]);
  const [fieldId, setFieldId] = useState(null);
  const [forecast, setForecast] = useState([]);

  const [waterVolume, setWaterVolume] = useState("");
  const [lai, setLai] = useState("");
  const [date, setDate] = useState("2026-01-14T06:00");

  /* ---------------- FETCH FIELD LIST ---------------- */
  useEffect(() => {
    console.log("FETCHING FIELD LIST");

    fetch("http://127.0.0.1:8000/field_list")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("FIELD LIST DATA:", data);

        if (!Array.isArray(data.fields)) {
          throw new Error("Invalid field_list response");
        }

        setFields(data.fields);

        if (data.fields.length > 0) {
          setFieldId(data.fields[0]);
        }
      })
      .catch((err) => {
        console.error("FIELD LIST FETCH ERROR:", err);
      });
  }, []);

  /* ---------------- FETCH FORECAST ---------------- */
  useEffect(() => {
    if (fieldId === null) return;

    console.log("FETCHING FORECAST FOR FIELD", fieldId);

    fetch(`http://127.0.0.1:8000/forecast?field_id=${fieldId}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("FORECAST DATA:", data);

        if (!Array.isArray(data.list1) || !Array.isArray(data.list2)) {
          throw new Error("Invalid forecast response");
        }

        const merged = data.list1.map((v, i) => ({
          hour: i,
          value1: v,
          value2: data.list2[i],
        }));

        setForecast(merged);
      })
      .catch((err) => {
        console.error("FORECAST FETCH ERROR:", err);
        setForecast([]);
      });
  }, [fieldId]);

  /* ---------------- ADD IRRIGATION ---------------- */
  const addIrrigation = () => {
    if (!fieldId) return;

    fetch(
      `http://127.0.0.1:8000/add_irr?field_id=${fieldId}&date=${date.replace(
        "T",
        " "
      )}:00&water_volume=${waterVolume}`,
      { method: "POST" }
    );
  };

  /* ---------------- ADD LAI ---------------- */
  const addLai = () => {
    if (!fieldId) return;

    fetch(
      `http://127.0.0.1:8000/add_lai?field_id=${fieldId}&date=${date.replace(
        "T",
        " "
      )}:00&lai=${lai}`,
      { method: "POST" }
    );
  };

  /* ---------------- RENDER ---------------- */
  return (
    <div style={{ maxWidth: 900, margin: "auto", padding: 20 }}>
      <h1>Irrigation Dashboard</h1>

      {/* -------- FIELD SELECT -------- */}
      <div style={{ marginBottom: 20 }}>
        <label>
          Field:&nbsp;
          <select
            value={fieldId ?? ""}
            onChange={(e) => setFieldId(Number(e.target.value))}
          >
            {fields.map((f) => (
              <option key={f} value={f}>
                Field {f}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* -------- FORECAST CHART -------- */}
      <div style={{ width: "100%", height: 300, border: "1px solid #ccc" }}>
        <ResponsiveContainer>
          <LineChart data={forecast}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Line dataKey="value1" />
            <Line dataKey="value2" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* -------- INPUTS -------- */}
      <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
        <input
          type="number"
          placeholder="Water volume"
          value={waterVolume}
          onChange={(e) => setWaterVolume(e.target.value)}
        />

        <input
          type="number"
          placeholder="LAI"
          value={lai}
          onChange={(e) => setLai(e.target.value)}
        />

        <input
          type="datetime-local"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>

      {/* -------- BUTTONS -------- */}
      <div style={{ marginTop: 15 }}>
        <button onClick={addIrrigation} style={{ marginRight: 10 }}>
          Add Irrigation
        </button>
        <button onClick={addLai}>Add LAI</button>
      </div>
    </div>
  );
}
