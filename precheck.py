import time
import requests
import streamlit as st
import streamlit.components.v1 as components

# Hide header link icons
st.markdown(
    """
    <style>
    /* Hide anchor link icons next to titles and headers */
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    a.header-anchor {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(
    page_title="Shisa Kanko Examination - System Readiness Check",
    page_icon="🛠️",
    layout="centered"
)

st.title("🛠️ Pre-Exam System Readiness Check")
st.write("Please run this system check on the computer and network you intend to use for the examination.")

st.markdown("""
<style>
    .metric-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-bottom: 10px;
    }
    .status-pass { color: #198754; font-weight: bold; }
    .status-fail { color: #dc3545; font-weight: bold; }
    .status-warn { color: #ffc107; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Session state to store diagnostic results from client JS
if "diag_results" not in st.session_state:
    st.session_state.diag_results = None

# Receive data back from embedded JS component via Streamlit query parameters or custom JS post
diag_data = st.query_params.to_dict()

# Embedded Client-Side JavaScript Diagnostic Engine
components.html(
    """
    <div id="diagnostic-status" style="font-family: sans-serif; padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
        🔍 Running Client-Side Diagnostics... Please wait.
    </div>

    <script>
    async function runDiagnostics() {
        const results = {
            isMobile: false,
            browserName: "Unknown",
            cameraAccess: false,
            imgbbAccessible: false,
            latencyMs: 0,
            overallPass: false,
            failureReasons: []
        };

        // 1. Device Detection (Mobile/Tablet vs Desktop)
        const ua = navigator.userAgent;
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)) {
            results.isMobile = true;
            results.failureReasons.push("Mobile/Tablet device detected. Desktop or Laptop computer is required.");
        }

        // 2. Browser Detection
        if (ua.indexOf("Chrome") > -1 && ua.indexOf("Edg") === -1) {
            results.browserName = "Google Chrome";
        } else if (ua.indexOf("Edg") > -1) {
            results.browserName = "Microsoft Edge";
        } else if (ua.indexOf("Safari") > -1 && ua.indexOf("Chrome") === -1) {
            results.browserName = "Safari";
        } else {
            results.browserName = "Other";
        }

        // 3. Camera Access Permission Check
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            results.cameraAccess = true;
            // Stop tracks immediately after testing
            stream.getTracks().forEach(track => track.stop());
        } catch (err) {
            results.cameraAccess = false;
            results.failureReasons.push("Camera access blocked or device missing. Please grant camera permission.");
        }

        // 4. API Reachability & Network Latency Check (api.imgbb.com)
        const startTime = performance.now();
        try {
            const res = await fetch("https://api.imgbb.com/1/upload", { method: "OPTIONS" });
            const endTime = performance.now();
            results.latencyMs = Math.round(endTime - startTime);
            results.imgbbAccessible = true;
        } catch (err) {
            results.imgbbAccessible = false;
            results.failureReasons.push("Unable to reach photo submission server (api.imgbb.com). Check network/firewall/VPN settings.");
        }

        // Evaluate overall status
        results.overallPass = !results.isMobile && results.cameraAccess && results.imgbbAccessible;

        // Render summary inside component
        const statusDiv = document.getElementById("diagnostic-status");
        if (results.overallPass) {
            statusDiv.innerHTML = "<h3 style='color: green;'>✅ System Readiness Passed!</h3>";
        } else {
            statusDiv.innerHTML = "<h3 style='color: red;'>❌ System Readiness Failed</h3><ul>" + 
                results.failureReasons.map(r => "<li>" + r + "</li>").join("") + "</ul>";
        }

        // Send results to parent Streamlit state via URL parameter sync button
        window.parent.postMessage({ type: "DIAG_COMPLETE", data: results }, "*");
    }

    // Trigger diagnostics on load
    runDiagnostics();
    </script>
    """,
    height=160
)

st.divider()
st.subheader("Diagnostic Criteria Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🖥️ Device & Browser")
    st.markdown("- **Approved Device:** Desktop / Laptop (Mac or PC)")
    st.markdown("- **Prohibited Device:** Smartphones & Tablets")
    st.markdown("- **Recommended Browser:** Google Chrome or Microsoft Edge")

with col2:
    st.markdown("### 🌐 Network & Hardware")
    st.markdown("- **Webcam:** Functional & Permissions Granted")
    st.markdown("- **API Route:** Unblocked access to `api.imgbb.com`")
    st.markdown("- **VPN:** Must be turned OFF")

st.divider()

# Backend Action Checklist
st.subheader("Candidate Pre-Exam Self-Verification")

c1 = st.checkbox("I am using a private home network (Not Hotel / Office Wi-Fi)")
c2 = st.checkbox("I have disabled all active VPNs and Proxy extensions")
c3 = st.checkbox("I am using Google Chrome or Microsoft Edge")

# if st.button("Proceed to Official Examination Portal", type="primary"):
all_verified = c1 and c2 and c3

if all_verified:
     st.link_button(
        "Proceed to Official Examination Portal ➡️",
        "https://exam2.shisakanko.org/",
        type="primary"
        )
else:
    if st.button("Proceed to Official Examination Portal", type="primary"):
        st.error("Please confirm all self-verification checkboxes before attempting the exam.")


st.divider()
