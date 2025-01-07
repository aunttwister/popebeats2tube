// instantTuneService.js
import apiClient from './apiClient.ts';
import { TuneDTO } from '../types/dto';

export const createBatchInstant = async (instants: TuneDTO[]): Promise<TuneDTO[]> => {
  const response = await apiClient.post('/instant-tune/batch', instants);
  return response.data;
};
