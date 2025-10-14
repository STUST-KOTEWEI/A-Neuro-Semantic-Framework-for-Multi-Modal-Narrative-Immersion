// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAzv4PLTCixkRnkPh1ZqeWs79rr44OUWbU",
  authDomain: "aireader-teweiko.firebaseapp.com",
  projectId: "aireader-teweiko",
  storageBucket: "aireader-teweiko.firebasestorage.app",
  messagingSenderId: "1065930878737",
  appId: "1:1065930878737:web:d3024e31342aa4fad926b0",
  measurementId: "G-B53Q7RMYBN"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
