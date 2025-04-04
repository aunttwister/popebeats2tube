import apiClient from './apiClient.ts';
import { TuneDTO } from '../types/dto';

export const getSchedules = async (page = 1, limit = 10, filters = {}) => {
  const params = {
    page: Number(page),
    limit: Number(limit),
    ...filters, // adds start_date, end_date, executed if provided
  };

  console.log(`${process.env.REACT_APP_API_BASE_URL}/scheduled-tune`, params);

  const response = await apiClient.get('/scheduled-tune', { params });
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
