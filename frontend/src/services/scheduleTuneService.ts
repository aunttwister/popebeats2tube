import apiClient from './apiClient.ts';
import { TuneDTO } from '../types/dto';

export const getSchedules = async (page = 1, limit = 10) => {
  const response = await apiClient.get('/scheduled-tune', {
    params: { page: Number(page), limit: Number(limit) },
  });
  return response.data;
};

export const createBatchSchedule = async (schedules: TuneDTO[]): Promise<TuneDTO[]> => {
  const response = await apiClient.post('/scheduled-tune/batch', schedules);
  return response.data;
};

export const editSchedule = async (id: bigint, schedule: TuneDTO): Promise<TuneDTO> => {
  const response = await apiClient.put(`/scheduled-tune/${id}`, schedule);
  return response.data;
};

export const removeSchedule = async (id: bigint): Promise<void> => {
  await apiClient.delete(`/scheduled-tune/${id}`);
};
