// instantTuneService.js
import apiClient from './apiClient.ts';
import { TuneDTO } from '../types/dto.ts';

export const createInstantTunes = async (instants: TuneDTO[]): Promise<TuneDTO[]> => {
  const response = await apiClient.post('/tune-ops/instant', instants);
  return response.data;
};

export const getSchedules = async (page = 1, limit = 10, filters = {}) => {
  const params = {
    page: Number(page),
    limit: Number(limit),
    ...filters, // adds start_date, end_date, executed if provided
  };

  const response = await apiClient.get('/tune-ops', { params });
  return response.data;
};

export const createScheduledTunes = async (schedules: TuneDTO[]): Promise<TuneDTO[]> => {
  const response = await apiClient.post('/tune-ops/schedule', schedules);
  return response.data;
};

export const editSchedule = async (id: bigint, schedule: TuneDTO): Promise<TuneDTO> => {
  const response = await apiClient.put(`/tune-ops/${id}`, schedule);
  return response.data;
};

export const removeSchedule = async (id: bigint): Promise<void> => {
  await apiClient.delete(`/tune-ops/${id}`);
};
