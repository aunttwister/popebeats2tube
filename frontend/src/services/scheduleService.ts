import apiClient from './apiClient.ts';
import { ScheduleDTO } from '../types/dto';

export const getSchedules = async (page = 1, limit = 10) => {
  const response = await apiClient.get('/schedule-upload', {
    params: { page: Number(page), limit: Number(limit) },
  });
  return response.data;
};

export const createSchedule = async (schedule: ScheduleDTO): Promise<ScheduleDTO> => {
  const response = await apiClient.post('/schedule-upload', schedule);
  return response.data;
};

export const createBatchSchedule = async (schedules: ScheduleDTO[]): Promise<ScheduleDTO[]> => {
  console.log(schedules)
  const response = await apiClient.post('/schedule-upload/batch', schedules);
  return response.data;
};

export const editSchedule = async (id: bigint, schedule: ScheduleDTO): Promise<ScheduleDTO> => {
  const response = await apiClient.put(`/schedule-upload/${id}`, schedule);
  return response.data;
};

export const removeSchedule = async (id: bigint): Promise<void> => {
  await apiClient.delete(`/schedule-upload/${id}`);
};
