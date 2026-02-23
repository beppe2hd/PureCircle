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
  Label,
} from "recharts";
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';

export default function IrrigationDashboard() {
  /* ---------------- STATE ---------------- */
  const [fields, setFields] = useState([]);
  const [fieldId, setFieldId] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [irrigation, setIrrigation] = useState(null);
  const [irr_dur, setIrr_dur] = useState(null);
  const [irr_vol, setIrr_vol] = useState(null);
  const [irr_time, setIrr_time] = useState(null);


  /* ---------------- FETCH FIELD LIST ---------------- */
  useEffect(() => {
    console.log("FETCHING FIELD LIST");

    fetch("https://api-purecircle.ngrok.app/field_list")
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

    fetch(`https://api-purecircle.ngrok.app/forecast?field_id=${fieldId}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("FORECAST DATA:", data);

        if (
          !Array.isArray(data.list1) ||
          !Array.isArray(data.list2) ||
          !Array.isArray(data.data_index)
        ) {
          throw new Error("Invalid forecast response");
        }

        const merged = data.list1.map((v, i) => ({
          hour: data.data_index[i],  // use provided index
          value1: v,
          value2: data.list2[i],
        }));

        setForecast(merged);
        setIrrigation(data.irrigation);
        setIrr_dur(data.duration);
        setIrr_vol(data.volume);
        setIrr_time(data.time);
      })
      .catch((err) => {
        console.error("FORECAST FETCH ERROR:", err);
        setForecast([]);
        setIrrigation(null);
      });
  }, [fieldId]);


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
                            Plot {f}
                          </option>
                        ))}
                      </Form.Select>
                    </Col>
                  </Row>


                  {/* -------- FORECAST CHART -------- */}
                  <Row>
                    <Col>
                      <div style={{ width: "100%", height: 500, border: "1px solid #ccc" }}>
                        <ResponsiveContainer>
                          <LineChart data={forecast}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                              dataKey="hour"
                              angle={-45} 
                              tick={{ fontSize: 9 }}
                            >
                              <Label
                                value="Date/Hours"
                                position="insideBottom"
                                offset={-10}
                              />
                            </XAxis>
                            <YAxis 
                              domain={[10, 46]} 
                              tickCount={20}
                            >
                              <Label
                                value="Soil Moisture"
                                angle={-90}
                                position="insideLeft"
                              />
                            </YAxis> 
                            <Tooltip />
                            <Line dataKey="value1" name="Within Line" stroke="#1f77b4" strokeWidth={2} />
                            {/*<Line dataKey="value2" stroke="#ff7f0e" strokeWidth={2} />*/}
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </Col>
                  </Row>
                  <Row className="justify-content-center my-4">
                    <Col md="4">
                      {irrigation === 1
                        ? <Alert variant="primary">
                          Irrigate for {irr_dur != null ? Math.round(irr_dur) : "-"} minutes befor the next {irr_time != null ? irr_time : "-"} hour/hours
                        </Alert>
                        : irrigation === 0
                          ? <Alert variant="secondary">
                            Irrigation not required
                          </Alert>
                          : ""}
                    </Col>
                  </Row>
                </Col>
              </Row>
            </Container>
          </Col>
        </Row>
      </Container>
    </>


  );
}
