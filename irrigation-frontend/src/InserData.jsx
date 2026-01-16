import { useEffect, useState } from "react";
import { Link } from "react-router-dom";


export default function IrrigationDashboard() {
  /* ---------------- STATE ---------------- */
  const [fields, setFields] = useState([]);
  const [fieldId, setFieldId] = useState(null);

  const [waterVolume, setWaterVolume] = useState("");
  const [lai, setLai] = useState("");
  const [date, setDate] = useState(() => {
    const now = new Date();
    now.setHours(6, 0, 0, 0); // 06:00:00.000
    return now.toISOString().slice(0, 16);
  });
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

      </main>
    </div>
    // <div style={{ maxWidth: 900, margin: "auto", padding: 20 }}>
    //   <h1>Irrigation Dashboard</h1>

    // {/* -------- FIELD SELECT -------- */}
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

    // {/* -------- INPUTS -------- */}
    // <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
    //   <input
    //     type="number"
    //     placeholder="Water volume"
    //     value={waterVolume}
    //     onChange={(e) => setWaterVolume(e.target.value)}
    //   />

    //   <input
    //     type="number"
    //     placeholder="LAI"
    //     value={lai}
    //     onChange={(e) => setLai(e.target.value)}
    //   />

    //   <input
    //     type="datetime-local"
    //     value={date}
    //     onChange={(e) => setDate(e.target.value)}
    //   />
    // </div>

    // {/* -------- BUTTONS -------- */}
    // <div style={{ marginTop: 15 }}>
    //   <button onClick={addIrrigation} style={{ marginRight: 10 }}>
    //     Add Irrigation
    //   </button>
    //   <button onClick={addLai}>Add LAI</button>
    // </div>
    // </div>
  );
}
