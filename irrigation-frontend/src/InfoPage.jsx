import { Link } from "react-router-dom";
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';


export default function InfoPage() {
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
                  <section>
                    <img src="src/img/logo_purecircles.png" alt="immagine"></img>
                    <p>
                      PureCircles main goal is to close water -, energy-, and nutrient cycles by AI-assisted integration of high-end solar technology, hydroponic systems, climate resilien crops, and smart agrotechnical management strategies.
                    </p>
                    <img src="src/img/csm_purecircles_concept.jpg" alt="immagine"></img>
                  </section>
                </Col>
              </Row>
            </Container>
          </Col>
        </Row>
      </Container>
    </>
  );
}


