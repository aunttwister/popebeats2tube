import apiClient from './apiClient';
import { TuneDTO } from '../types/dto';

export const uploadTune = async (tune: TuneDTO): Promise<void> => {
  const formData = new FormData();
  formData.append('id', tune.id.toString());
  formData.append('title', tune.title);
  formData.append('description', tune.description);
  formData.append('audio_file', tune.audio_file);
  formData.append('image_file', tune.image_file);

  await apiClient.post('/upload_tune/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const batchUploadTunes = async (tunes: TuneDTO[]): Promise<void> => {
  const formData = new FormData();
  tunes.forEach((tune, index) => {
    formData.append(`tunes[${index}][id]`, tune.id.toString());
    formData.append(`tunes[${index}][title]`, tune.title);
    formData.append(`tunes[${index}][description]`, tune.description);
    formData.append(`tunes[${index}][audio_file]`, tune.audio_file);
    formData.append(`tunes[${index}][image_file]`, tune.image_file);
  });

  await apiClient.post('/upload_tune/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
