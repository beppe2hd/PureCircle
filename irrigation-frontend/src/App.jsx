// import IrrigationDashboard from "./IrrigationDashboard";

// function App() {
//   return <IrrigationDashboard />;
// }

// export default App;

import { BrowserRouter, Routes, Route } from "react-router-dom";
import InfoPage from "./InfoPage";
import InserData from "./InserData";
import ReadSM from "./ReadSM";
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<InfoPage />} />
        <Route path="/inserdata" element={<InserData />} />
        <Route path="/readsm" element={<ReadSM />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
