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
import DropzoneField from './DropzoneField'; // Import the separated component
import './UploadContainer.css'; // Import external CSS
import config from '../../config.json';

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
      setTags([...tags, e.target.value.trim()]);
      e.target.value = '';
    }
  };

  const handleTagDelete = (tagToDelete) => {
    setTags(tags.filter((tag) => tag !== tagToDelete));
  };

  return (
    <Box className="upload-container">
      <Typography variant="subtitle1">Upload Container {containerIndex + 1}</Typography>

      <DropzoneField
        onDrop={(files) => onDropAudio(containerIndex, files)}
        label="Drag and drop audio file here"
        file={audioFile}
        acceptedFileTypes={audioConfig.accept}
        maxFileSize={audioConfig.maxFileSize}
        isValid={!errors.audio}
        setIsValid={() => {}} // no-op unless you need internal control
      />
      {errors.audio && (
        <Typography variant="caption" color="error">
          {errors.audio}
        </Typography>
      )}


      <DropzoneField
        onDrop={(files) => onDropImage(containerIndex, files)}
        label="Drag and drop image file here"
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
        label="Add Tags (Press Enter to Add)"
        onKeyDown={handleTagKeyDown}
      />
      <Box className="tags-container">
        {tags.map((tag, index) => (
          <Chip key={index} label={tag} onDelete={() => handleTagDelete(tag)} />
        ))}
      </Box>

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
