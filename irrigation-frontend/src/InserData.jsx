import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import FloatingLabel from 'react-bootstrap/FloatingLabel';


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
    <>
      <Navbar bg="dark" data-bs-theme="dark" expand="lg">
        <Container>
          <Navbar.Brand href="/">Purecircle</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="/">Home</Nav.Link>
              <Nav.Link href="/inserdata">Insert Data</Nav.Link>
              <Nav.Link href="/readsm">Read SM</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid>
        <Row>
          <Col>
            <Container>
              <Row>
                <Col className="text-center">

                  {/* Contenuto principale */}
>
                  {/* -------- FIELD SELECT -------- */}
                  <Row className="justify-content-center my-4">
                    <Col md="4">
                      <Form.Select
                        size="lg"
                        value={fieldId ?? ""}
                        onChange={(e) => setFieldId(Number(e.target.value))}
                      >
                        {fields.map((f) => (
                          <option key={f} value={f}>
                            Field {f}
                          </option>
                        ))}
                      </Form.Select>
                    </Col>
                  </Row>


                  <FloatingLabel
                    controlId="water-volume"
                    label="Water volume"
                    className="mb-3"
                  >
                    <Form.Control type="number" placeholder="Water volume" value={waterVolume}
                      onChange={(e) => setWaterVolume(e.target.value)} />
                  </FloatingLabel>
                  <FloatingLabel
                    controlId="lai"
                    label="LAI"
                    className="mb-3"
                  >
                    <Form.Control type="number" placeholder="LAI" value={lai}
                      onChange={(e) => setLai(e.target.value)} />
                  </FloatingLabel>

                  {/* -------- INPUTS -------- */}
                  <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
                    {/* <input
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
                    /> */}

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

                </Col>
              </Row>
            </Container>
          </Col>
        </Row>
      </Container>
    </>


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
