import { useState, useRef, useEffect } from "react";
import {
  Wrench,
  Send,
  Upload,
  Calendar,
  AlertTriangle,
  Clock,
  DollarSign,
  CheckCircle2,
  FileCheck,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import "./App.css";

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hello! I am your AutoMech AI diagnostic assistant. Tell me what symptoms or troubles your vehicle is having.",
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [category, setCategory] = useState(null);
  const [state, setState] = useState("gathering");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [diagnosing, setDiagnosing] = useState(false);
  const [booking, setBooking] = useState(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [bookingForm, setBookingForm] = useState({
    customer_name: "",
    phone: "",
    vehicle: "",
    preferred_slot: "",
  });
  const [bookingLoading, setBookingLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, diagnosis, booking]);

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputText.trim() || loading) return;

    const userText = inputText.trim();
    setInputText("");
    setErrorMsg("");

    const newHistory = [...messages, { role: "user", text: userText }];
    setMessages(newHistory);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: userText,
        }),
      });

      if (!res.ok) throw new Error("Failed to send message.");

      const data = await res.json();
      setConversationId(data.conversation_id);
      setCategory(data.category);
      setState(data.state);
      setMessages(data.history);
    } catch (err) {
      setErrorMsg(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !conversationId) return;

    setUploading(true);
    setErrorMsg("");

    const formData = new FormData();
    formData.append("conversation_id", conversationId);
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed. Check file type and size.");

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          text: `[Uploaded Media: ${data.original_filename}]`,
        },
        {
          role: "bot",
          text: "I received your upload and have added the visual/audio data to your diagnostic profile.",
        },
      ]);
    } catch (err) {
      setErrorMsg(err.message || "Error uploading media.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleGenerateDiagnosis = async () => {
    if (!conversationId || diagnosing) return;
    setDiagnosing(true);
    setErrorMsg("");

    try {
      const res = await fetch(`${API_BASE}/diagnosis/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation_id: conversationId }),
      });

      if (!res.ok) throw new Error("Diagnosis evaluation failed.");

      const data = await res.json();
      setDiagnosis(data);
      setState("diagnosed");
    } catch (err) {
      setErrorMsg(err.message || "Failed to generate diagnosis.");
    } finally {
      setDiagnosing(false);
    }
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    if (!diagnosis?.id || bookingLoading) return;

    setBookingLoading(true);
    setErrorMsg("");

    try {
      const res = await fetch(`${API_BASE}/booking/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          diagnosis_id: diagnosis.id,
          ...bookingForm,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData?.error?.message || "Failed to create booking.");
      }

      const data = await res.json();
      setBooking(data);
      setShowBookingModal(false);
      setState("booked");
    } catch (err) {
      setErrorMsg(err.message || "Booking submission failed.");
    } finally {
      setBookingLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-brand">
          <div className="logo-badge">
            <Wrench className="icon-main" />
          </div>
          <div>
            <h1>AutoMech AI</h1>
            <p className="subtitle">Virtual Automotive Diagnostic Specialist</p>
          </div>
        </div>
        <div className="header-status">
          {category && <span className="badge category-badge">{category.toUpperCase()}</span>}
          <span className="badge state-badge">{state.replace("_", " ").toUpperCase()}</span>
        </div>
      </header>

      {errorMsg && <div className="error-banner">{errorMsg}</div>}

      <div className="main-layout">
        <section className="chat-section">
          <div className="chat-window">
            {messages.map((m, idx) => (
              <div key={idx} className={`message-bubble ${m.role}`}>
                <div className="bubble-content">{m.text}</div>
              </div>
            ))}
            {loading && (
              <div className="message-bubble bot typing">
                <span>Analyzing symptoms...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="action-bar">
            {conversationId && (
              <>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  style={{ display: "none" }}
                  accept="image/*,audio/*,video/*"
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={uploading}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload size={16} />
                  {uploading ? "Uploading..." : "Upload Media"}
                </button>
              </>
            )}

            {conversationId && state !== "diagnosed" && state !== "booked" && (
              <button
                type="button"
                className="btn btn-accent"
                disabled={diagnosing}
                onClick={handleGenerateDiagnosis}
              >
                <Sparkles size={16} />
                {diagnosing ? "Evaluating..." : "Generate Diagnosis"}
              </button>
            )}
          </div>

          <form className="chat-input-bar" onSubmit={handleSendMessage}>
            <input
              type="text"
              placeholder="Describe symptoms, noises, leaks, or vehicle behaviors..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" disabled={loading || !inputText.trim()}>
              <Send size={16} />
            </button>
          </form>
        </section>

        <aside className="sidebar">
          {diagnosis ? (
            <div className="card diagnosis-card">
              <div className="card-header">
                <FileCheck size={20} className="card-icon" />
                <h3>Diagnostic Evaluation</h3>
              </div>

              <div className="diag-item">
                <span className="diag-label">Summary</span>
                <p className="diag-value">{diagnosis.summary}</p>
              </div>

              <div className="diag-item">
                <span className="diag-label">Probable Cause</span>
                <p className="diag-value">{diagnosis.probable_cause}</p>
              </div>

              <div className="diag-meta-grid">
                <div className="meta-box">
                  <AlertTriangle size={16} className={`severity-icon ${diagnosis.severity}`} />
                  <div>
                    <span className="meta-title">Severity</span>
                    <span className={`meta-data severity-${diagnosis.severity}`}>
                      {diagnosis.severity.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="meta-box">
                  <Clock size={16} />
                  <div>
                    <span className="meta-title">Est. Time</span>
                    <span className="meta-data">{diagnosis.estimated_time}</span>
                  </div>
                </div>

                <div className="meta-box">
                  <DollarSign size={16} />
                  <div>
                    <span className="meta-title">Est. Cost</span>
                    <span className="meta-data">{diagnosis.estimated_cost}</span>
                  </div>
                </div>
              </div>

              <div className="diag-item">
                <span className="diag-label">Recommended Service</span>
                <p className="diag-value service-highlight">{diagnosis.suggested_service}</p>
              </div>

              {!booking ? (
                <button
                  type="button"
                  className="btn btn-primary btn-block"
                  onClick={() => setShowBookingModal(true)}
                >
                  <Calendar size={16} />
                  Book Certified Mechanic
                </button>
              ) : (
                <div className="booking-badge-confirmed">
                  <CheckCircle2 size={16} />
                  Appointment Booked
                </div>
              )}
            </div>
          ) : (
            <div className="card placeholder-card">
              <Sparkles size={36} className="placeholder-icon" />
              <h3>Interactive Triage</h3>
              <p>
                Chat with the AI assistant to isolate symptoms, or upload dashboard photos and audio clips
                to trigger a structured inspection report.
              </p>
            </div>
          )}

          {booking && (
            <div className="card booking-card">
              <div className="card-header">
                <CheckCircle2 size={20} className="card-icon success" />
                <h3>Appointment Confirmed</h3>
              </div>
              <p className="booking-row">
                <strong>Booking ID:</strong> <span>{booking.id.slice(0, 8)}...</span>
              </p>
              <p className="booking-row">
                <strong>Customer:</strong> <span>{booking.customer_name}</span>
              </p>
              <p className="booking-row">
                <strong>Phone:</strong> <span>{booking.phone}</span>
              </p>
              <p className="booking-row">
                <strong>Vehicle:</strong> <span>{booking.vehicle}</span>
              </p>
              <p className="booking-row">
                <strong>Preferred Slot:</strong> <span>{booking.preferred_slot}</span>
              </p>
              <div className="booking-status-tag">{booking.status.toUpperCase()}</div>
            </div>
          )}
        </aside>
      </div>

      {showBookingModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Schedule Service Appointment</h3>
              <button
                type="button"
                className="close-btn"
                onClick={() => setShowBookingModal(false)}
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleBookingSubmit} className="modal-form">
              <div className="form-group">
                <label>Customer Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={bookingForm.customer_name}
                  onChange={(e) =>
                    setBookingForm({ ...bookingForm, customer_name: e.target.value })
                  }
                />
              </div>

              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. +1 555-0199"
                  value={bookingForm.phone}
                  onChange={(e) =>
                    setBookingForm({ ...bookingForm, phone: e.target.value })
                  }
                />
              </div>

              <div className="form-group">
                <label>Vehicle (Year / Make / Model)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 2021 Toyota RAV4"
                  value={bookingForm.vehicle}
                  onChange={(e) =>
                    setBookingForm({ ...bookingForm, vehicle: e.target.value })
                  }
                />
              </div>

              <div className="form-group">
                <label>Preferred Time Slot</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tomorrow at 10:00 AM"
                  value={bookingForm.preferred_slot}
                  onChange={(e) =>
                    setBookingForm({ ...bookingForm, preferred_slot: e.target.value })
                  }
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowBookingModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={bookingLoading}
                >
                  {bookingLoading ? "Booking..." : "Confirm Appointment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}