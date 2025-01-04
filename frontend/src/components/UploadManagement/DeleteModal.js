import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Button } from '@mui/material';

function DeleteModal({ open, onClose, onConfirm, selectedUpload }) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Confirm Delete</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete the schedule titled "{selectedUpload?.video_title}"?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>No</Button>
        <Button onClick={onConfirm} color="error">
          Yes
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default DeleteModal;
