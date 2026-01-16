import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
  const styles = {
    page: {
      fontFamily: "Arial, sans-serif",
      minHeight: "100vh",
      backgroundColor: "#f4f6f8",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "12px 24px",
      backgroundColor: "#1f2937",
      color: "white",
    },
    logo: {
      margin: 0,
    },
    nav: {
      display: "flex",
      gap: "16px",
    },
    link: {
      color: "white",
      textDecoration: "none",
      fontWeight: "bold",
    },
    main: {
      padding: "40px",
      display: "flex",
      justifyContent: "center",
    },
    card: {
      backgroundColor: "white",
      padding: "24px",
      borderRadius: "8px",
      width: "100%",
      maxWidth: "600px",
      boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    },
  };



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


  /* ---------------- RENDER ---------------- */
  return (

    <div style={styles.page}>
      {/* Barra superiore */}
      <header style={styles.header}>
        <h2 style={styles.logo}>Pure Circle</h2>

        <nav style={styles.nav}>
          <Link to="/" style={styles.link}>
            Home
          </Link>
          <Link to="/inserdata" style={styles.link}>
            Inserisci Dati
          </Link>
          <Link to="/readsm" style={styles.link}>
            Leggi SM
          </Link>
        </nav>
      </header>

      {/* Contenuto principale */}
      <main style={styles.main}>
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

      </main>
    </div>

    // <div style={{ maxWidth: 900, margin: "auto", padding: 20 }}>

    //   <h1>Irrigation Dashboard</h1>

    //   {/* -------- FIELD SELECT -------- */}
    // <div style={{ marginBottom: 20 }}>
    //   <label>
    //     Field:&nbsp;
    //     <select
    //       value={fieldId ?? ""}
    //       onChange={(e) => setFieldId(Number(e.target.value))}
    //     >
    //       {fields.map((f) => (
    //         <option key={f} value={f}>
    //           Field {f}
    //         </option>
    //       ))}
    //     </select>
    //   </label>
    // </div>

    // {/* -------- FORECAST CHART -------- */}
    // <div style={{ width: "100%", height: 300, border: "1px solid #ccc" }}>
    //   <ResponsiveContainer>
    //     <LineChart data={forecast}>
    //       <CartesianGrid strokeDasharray="3 3" />
    //       <XAxis dataKey="hour" />
    //       <YAxis />
    //       <Tooltip />
    //       <Line dataKey="value1" />
    //       <Line dataKey="value2" />
    //     </LineChart>
    //   </ResponsiveContainer>
    // </div>

    // </div>
  );
}
