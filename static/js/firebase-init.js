import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyANXKF_qGWe1aDo-QGxPItdQ4azFUs1Q4Y",
  authDomain: "marketing-job-hub.firebaseapp.com",
  projectId: "marketing-job-hub",
  storageBucket: "marketing-job-hub.appspot.com",
  messagingSenderId: "550647396506",
  appId: "1:550647396506:web:04485035006276de808723"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { app, auth };
