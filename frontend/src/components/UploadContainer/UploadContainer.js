import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Typography,
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
import DropzoneField from './DropzoneField';
import './UploadContainer.css';
import config from '../../config.json';
import AudiotrackIcon from '@mui/icons-material/Audiotrack';
import ImageIcon from '@mui/icons-material/Image';
import Tooltip from '@mui/material/Tooltip';

function UploadContainer({ onDropAudio, onDropImage, onChange, containerIndex, audioFile, imageFile, errors = {} }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState([]);
  const [category, setCategory] = useState('');
  const [privacyStatus, setPrivacyStatus] = useState('private');
  const [embeddable, setEmbeddable] = useState(false);
  const [license, setLicense] = useState('youtube');
  const [categories, setCategories] = useState([]);

  const audioConfig = config.fileUpload.audio;
  const imageConfig = config.fileUpload.image;

  useEffect(() => {
    const fetchCategories = async () => {
      const mockCategories = [
        { id: '1', name: 'Film & Animation' },
        { id: '2', name: 'Music' },
        { id: '22', name: 'People & Blogs' },
      ];
      setCategories(mockCategories);
    };
    fetchCategories();
  }, []); // Runs only once when the component mounts
  
  useEffect(() => {
    // Avoid infinite updates by checking for changes
    const currentData = {
      title,
      description,
      tags,
      category,
      privacyStatus,
      embeddable,
      license,
      audio: audioFile,
      image: imageFile,
    };
  
    const hasChanged = JSON.stringify(currentData) !== JSON.stringify(previousDataRef.current);
  
    if (hasChanged) {
      previousDataRef.current = currentData; // Update the reference
      onChange(containerIndex, currentData);
    }
  }, [title, description, tags, category, privacyStatus, embeddable, license, audioFile, imageFile, containerIndex, onChange]);
  
  // Use a ref to store the previous data to avoid unnecessary calls
  const previousDataRef = React.useRef({});

  const handleTitleChange = (e) => {
    const newTitle = e.target.value;
    setTitle(newTitle);
  };

  const handleDescriptionChange = (e) => setDescription(e.target.value);

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter' && e.target.value.trim()) {
      e.preventDefault();
  
      const rawInput = e.target.value;
      const inputTags = rawInput
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0 && !tags.includes(tag)); // remove empty and duplicates
  
      setTags([...tags, ...inputTags]);
      e.target.value = '';
    }
  };

  const handleTagDelete = (tagToDelete) => {
    const index = tags.indexOf(tagToDelete);
    if (index !== -1) {
      const newTags = [...tags];
      newTags.splice(index, 1);
      setTags(newTags);
    }
  };

  return (
    <Box className="upload-container">
      <Typography variant="subtitle1">Upload Container {containerIndex + 1}</Typography>

      <DropzoneField
        onDrop={(files) => onDropAudio(containerIndex, files)}
        label={
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center">
            <AudiotrackIcon
              sx={{
                fontSize: 36,
                color: audioFile ? '#2ac759' : '#aaa',
              }}
            />
            <Typography variant="body2">Drag and drop audio file here</Typography>
            {audioFile && (
              <Typography variant="caption">Uploaded: {audioFile.name}</Typography>
            )}
          </Box>
        }
        file={audioFile}
        acceptedFileTypes={audioConfig.accept}
        maxFileSize={audioConfig.maxFileSize}
        isValid={!errors.audio}
        setIsValid={() => {}}
      />

      <DropzoneField
        onDrop={(files) => onDropImage(containerIndex, files)}
        label={
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center">
            <ImageIcon
              sx={{
                fontSize: 36,
                color: imageFile ? '#2ac759' : '#aaa',
              }}
            />
            <Typography variant="body2">Drag and drop image file here</Typography>
            {imageFile && (
              <Typography variant="caption">Uploaded: {imageFile.name}</Typography>
            )}
          </Box>
        }
        file={imageFile}
        acceptedFileTypes={imageConfig.accept}
        maxFileSize={imageConfig.maxFileSize}
        isValid={!errors.image}
        setIsValid={() => {}}
      />
      {errors.image && (
        <Typography variant="caption" color="error">
          {errors.image}
        </Typography>
      )}

      <TextField
        fullWidth
        margin="normal"
        label="YouTube Video Title"
        value={title}
        onChange={handleTitleChange}
        error={Boolean(errors.title)}
        helperText={errors.title}
      />

      <TextField
        fullWidth
        margin="normal"
        label="YouTube Video Description"
        multiline
        rows={3}
        value={description}
        onChange={handleDescriptionChange}
      />

      <TextField
        fullWidth
        margin="normal"
        label="Add Tags (Enter or space-separated)"
        onKeyDown={handleTagKeyDown}
      />
      {tags.length > 0 && (
      <Box sx={{ mt: 1, width: '100%', maxWidth: '100%' }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1,
            width: '100%',
            maxWidth: '100%',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Tags ({tags.length})
          </Typography>
          <Typography
            onClick={() => setTags([])}
            variant="caption"
            color="error"
            sx={{ cursor: 'pointer' }}
          >
            Clear All
          </Typography>
        </Box>

        <Box className="tags-wrapper">
          {tags.map((tag, index) => (
            <Tooltip key={index} title={tag}>
              <Chip
                label={tag}
                onDelete={() => handleTagDelete(tag)}
              />
            </Tooltip>
          ))}
        </Box>
      </Box>
    )}

      <FormControl fullWidth margin="normal" error={Boolean(errors.category)}>
        <FormLabel>Category</FormLabel>
        <Select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {categories.map((cat) => (
            <MenuItem key={cat.id} value={cat.id}>
              {cat.name}
            </MenuItem>
          ))}
        </Select>
        {errors.category && (
          <Typography variant="caption" color="error">
            {errors.category}
          </Typography>
        )}
      </FormControl>

      <Box className="radio-group-container">
        <FormControl className="radio-group">
          <FormLabel>Privacy Status</FormLabel>
          <RadioGroup
            row
            value={privacyStatus}
            onChange={(e) => setPrivacyStatus(e.target.value)}
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
            value={license}
            onChange={(e) => setLicense(e.target.value)}
          >
            <FormControlLabel value="youtube" control={<Radio />} label="YouTube" />
            <FormControlLabel value="creativeCommon" control={<Radio />} label="Creative Commons" />
          </RadioGroup>
        </FormControl>
      </Box>

      <Box>
        <FormControlLabel
          control={
            <Checkbox
              checked={embeddable}
              onChange={(e) => setEmbeddable(e.target.checked)}
            />
          }
          label="Embeddable"
        />
      </Box>
    </Box>
  );
}

export default UploadContainer;
