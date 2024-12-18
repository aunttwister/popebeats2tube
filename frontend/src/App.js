import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InstantUpload from './components/InstantUpload';
import ScheduledUpload from './components/ScheduledUpload';
import UploadManagement from './components/UploadManagement';

function App() {
  const [selectedTab, setSelectedTab] = useState(0);

  return (
    <div>
      <Navbar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
      {selectedTab === 0 && <InstantUpload />}
      {selectedTab === 1 && <ScheduledUpload />}
      {selectedTab === 2 && <UploadManagement />}
    </div>
  );
}

export default App;
