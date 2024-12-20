import apiClient from './apiClient';
import { ScheduleDTO } from '../types/dto';

export const getSchedules = async (page = 1, limit = 10): Promise<{
  data: ScheduleDTO[];
  current_page: number;
  total_pages: number;
}> => {
  const response = await apiClient.get('/schedule/get', {
    params: { page, limit },
  });
  return response.data;
};

export const createSchedule = async (schedule: ScheduleDTO): Promise<ScheduleDTO> => {
  const response = await apiClient.post('/schedule/create', schedule);
  return response.data;
};

export const editSchedule = async (id: bigint, schedule: ScheduleDTO): Promise<ScheduleDTO> => {
  const response = await apiClient.put(`/schedule/edit/${id}`, schedule);
  return response.data;
};

export const removeSchedule = async (id: bigint): Promise<void> => {
  await apiClient.delete(`/schedule/remove/${id}`);
};
