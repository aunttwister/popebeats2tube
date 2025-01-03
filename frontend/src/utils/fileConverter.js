const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      // Check if the file is empty (0 bytes)
      if (!file || file.size === 0) {
        reject(new Error('The file is empty.'));
        return;
      }
  
      if (!(file instanceof Blob)) {
        console.error('Invalid file object:', file);
        reject(new Error('Invalid file input. Expected a Blob or File.'));
        return;
      }
  
      const reader = new FileReader();
  
      reader.onload = () => {
        const result = reader.result;
        if (typeof result === 'string') {
          resolve(result.split(',')[1]); // Extract base64 string
        } else {
          reject(new Error('Failed to extract base64 string.'));
        }
      };
  
      reader.onerror = (error) => {
        console.error('FileReader Error:', error);
        reject(error);
      };
  
      reader.readAsDataURL(file); // Read file as a base64 data URL
    });
  };
  
  export const fileConverter = {
    fileToBase64,
  };
  