import { Link } from "react-router-dom";

export default function InfoPage() {
  return (
    <div style={styles.page}>
      {/* Barra superiore */}
      <header style={styles.header}>
        <h2 style={styles.logo}>Pure Circle</h2>

        <nav style={styles.nav}>
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
        <section style={styles.card}>
          <h3>General info</h3>
          <img src="src/img/logo_purecircles.png" alt="immagine"></img>
          <p>
            PureCircles main goal is to close water -, energy-, and nutrient cycles by AI-assisted integration of high-end solar technology, hydroponic systems, climate resilien crops, and smart agrotechnical management strategies.
          </p>
          <img src="src/img/csm_purecircles_concept.jpg" alt="immagine"></img>
        </section>
      </main>
    </div>
  );
}


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
