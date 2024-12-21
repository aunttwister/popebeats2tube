import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InstantUpload from './components/InstantUpload';
import ScheduledUpload from './components/ScheduledUpload';
import UploadManagement from './components/UploadManagement';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const [selectedTab, setSelectedTab] = useState(0);

  return (
    <div>
      <ToastContainer
        position="top-right"  // Default position
        autoClose={3000}      // Default auto-close duration (in milliseconds)
        hideProgressBar={false} // Show progress bar
        newestOnTop={true}    // Newest toast appears on top
        closeOnClick={true}   // Dismiss toast on click
        pauseOnHover={true}   // Pause auto-close on hover
        draggable={true}      // Allow dragging the toast
        theme="colored"       // Theme: 'light', 'dark', or 'colored'
      />
      <Navbar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
      {selectedTab === 0 && <InstantUpload />}
      {selectedTab === 1 && <ScheduledUpload />}
      {selectedTab === 2 && <UploadManagement />}
    </div>
  );
}

export default App;
