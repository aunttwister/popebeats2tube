import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  TextField,
  Box,
  FormControl,
  FormLabel,
  FormControlLabel,
  RadioGroup,
  Radio,
  Checkbox,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import '../UploadContainer/UploadContainer.css'; // Import external CSS

function EditModal({ open, onClose, onSave, editFormData, setEditFormData }) {
  const [tags, setTags] = useState(editFormData.tags || []);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    // Mock fetch categories - replace with API call if needed
    const fetchCategories = async () => {
      const mockCategories = [
        { id: '1', name: 'Film & Animation' },
        { id: '2', name: 'Music' },
        { id: '22', name: 'People & Blogs' },
      ];
      setCategories(mockCategories);
    };
    fetchCategories();

    setTags(editFormData.tags || []); // Sync tags state when editFormData changes
  }, [editFormData]);

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter' && e.target.value.trim()) {
      const updatedTags = [...tags, e.target.value.trim()];
      setTags(updatedTags);
      setEditFormData({ ...editFormData, tags: updatedTags });
      e.target.value = '';
    }
  };

  const handleTagDelete = (tagToDelete) => {
    const updatedTags = tags.filter((tag) => tag !== tagToDelete);
    setTags(updatedTags);
    setEditFormData({ ...editFormData, tags: updatedTags });
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Schedule</DialogTitle>
        <DialogContent>
          {/* Title Field */}
          <TextField
            label="YouTube Video Title"
            value={editFormData.video_title || ''}
            onChange={(e) => setEditFormData({ ...editFormData, video_title: e.target.value })}
            fullWidth
            margin="normal"
          />

          {/* Description Field */}
          <TextField
            fullWidth
            margin="normal"
            label="YouTube Video Description"
            multiline
            rows={3}
            value={editFormData.video_description || ''}
            onChange={(e) => setEditFormData({ ...editFormData, video_description: e.target.value })}
          />

          {/* Tags */}
          <TextField
            fullWidth
            margin="normal"
            label="Add Tags (Press Enter to Add)"
            onKeyDown={handleTagKeyDown}
          />
          <Box className="tags-container">
            {tags.map((tag, index) => (
              <Chip key={index} label={tag} onDelete={() => handleTagDelete(tag)} />
            ))}
          </Box>

          {/* Category */}
          <FormControl fullWidth margin="normal">
            <FormLabel>Category</FormLabel>
            <Select
              value={editFormData.category || ''}
              onChange={(e) => setEditFormData({ ...editFormData, category: e.target.value })}
            >
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.name}>
                  {cat.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Privacy and License */}
          <Box className="radio-group-container">
            <FormControl className="radio-group">
              <FormLabel>Privacy Status</FormLabel>
              <RadioGroup
                row
                value={editFormData.privacy_status || 'private'}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, privacy_status: e.target.value })
                }
              >
                <FormControlLabel value="public" control={<Radio />} label="Public" />
                <FormControlLabel value="private" control={<Radio />} label="Private" />
                <FormControlLabel value="unlisted" control={<Radio />} label="Unlisted" />
              </RadioGroup>
            </FormControl>

            <FormControl className="radio-group">
              <FormLabel>License</FormLabel>
              <RadioGroup
                row
                value={editFormData.license || 'youtube'}
                onChange={(e) => setEditFormData({ ...editFormData, license: e.target.value })}
              >
                <FormControlLabel value="youtube" control={<Radio />} label="YouTube" />
                <FormControlLabel value="creativeCommon" control={<Radio />} label="Creative Commons" />
              </RadioGroup>
            </FormControl>
          </Box>

          {/* Embeddable */}
          <Box sx={{ marginBottom: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={editFormData.embeddable || false}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, embeddable: e.target.checked })
                  }
                />
              }
              label="Embeddable"
            />
          </Box>

          {/* Upload Date and Time */}
          <MobileDateTimePicker
            label="Upload Date and Time"
            value={editFormData.upload_date || null}
            onChange={(date) => setEditFormData({ ...editFormData, upload_date: date })}
            textField={(params) => <TextField {...params} fullWidth margin="normal" />}
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
