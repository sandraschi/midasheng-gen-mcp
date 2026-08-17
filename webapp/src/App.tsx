import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import ApiDocs from "./pages/ApiDocs";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Help from "./pages/Help";
import Inbox from "./pages/Inbox";
import Logs from "./pages/Logs";
import Scenes from "./pages/Scenes";
import Settings from "./pages/Settings";
import Skills from "./pages/Skills";
import Tools from "./pages/Tools";

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/scenes" element={<Scenes />} />
          <Route path="/inbox" element={<Inbox />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/api-docs" element={<ApiDocs />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}
