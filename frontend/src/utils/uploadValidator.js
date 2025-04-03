export function validateContainer(container, includeUploadDate = false) {
    const errors = {};
    if (!container.audio) errors.audio = 'Audio file is required.';
    if (!container.image) errors.image = 'Image file is required.';
    if (!container.title || container.title.trim() === '')
      errors.title = 'Title is required.';
    if (!container.category || container.category.trim() === '')
      errors.category = 'Category is required.';
    if (includeUploadDate && !container.uploadDate)
      errors.uploadDate = 'Upload date is required.';
    return errors;
  }
  