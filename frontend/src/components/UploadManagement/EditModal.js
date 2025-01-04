import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button, TextField } from '@mui/material';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

function EditModal({ open, onClose, onSave, editFormData, setEditFormData }) {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Dialog open={open} onClose={onClose}>
        <DialogTitle>Edit Schedule</DialogTitle>
        <DialogContent>
          <TextField
            label="Title"
            value={editFormData.video_title}
            onChange={(e) => setEditFormData({ ...editFormData, video_title: e.target.value })}
            fullWidth
            margin="normal"
          />
          <MobileDateTimePicker
            label="Upload Date and Time"
            value={editFormData.upload_date} // Must be a Dayjs object
            onChange={(date) => setEditFormData({ ...editFormData, upload_date: date })} // Pass the Dayjs object directly
            renderInput={(params) => <TextField {...params} fullWidth margin="normal" />}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={onSave} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
}

export default EditModal;
