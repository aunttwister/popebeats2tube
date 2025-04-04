import React, { useEffect, useState } from 'react';
import {
  CircularProgress,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Box,
  Fade,
} from '@mui/material';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

import UploadTable from './UploadTable';
import PaginationControl from './PaginationControl';
import DeleteModal from './DeleteModal';
import EditModal from './EditModal';
import { getSchedules, editSchedule, removeSchedule } from '../../services/scheduleTuneService.ts';
import { toastHelper } from '../../utils/toastHelper';
import './UploadManagement.css';

function UploadManagement() {
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedUpload, setSelectedUpload] = useState(null);
  const [editFormData, setEditFormData] = useState({ video_title: '', upload_date: '' });

  const [beforeDate, setBeforeDate] = useState('');
  const [executedFilter, setExecutedFilter] = useState('all');

  const fetchSchedules = async (page) => {
    try {
      setLoading(true);
      setError(null);

      const filters = {
        upload_date_before: beforeDate ? dayjs(beforeDate).endOf('day').toISOString() : undefined,
        executed: executedFilter !== 'all' ? executedFilter : undefined,
      };

      const response = await getSchedules(page, 10, filters);
      setUploads(response.data.data || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (err) {
      setError('Failed to load uploads.');
      toastHelper.newMessage('error', err.title || 'Error', err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules(currentPage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, beforeDate, executedFilter]);

  const handlePageChange = (_, value) => setCurrentPage(value);

  const handleDeleteClick = (upload) => {
    setSelectedUpload(upload);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      if (selectedUpload) {
        await removeSchedule(selectedUpload.id);
        setUploads((prev) => prev.filter((u) => u.id !== selectedUpload.id));
      }
    } catch (err) {
      toastHelper.newMessage('error', err.title || 'Error', err.detail || 'Delete failed');
    } finally {
      setDeleteModalOpen(false);
    }
  };

  const handleEditClick = (upload) => {
    setSelectedUpload(upload);
    setEditFormData({
      video_title: upload.video_title || '',
      video_description: upload.video_description || '',
      upload_date: dayjs(upload.upload_date),
      tags: Array.isArray(upload.tags) ? upload.tags : JSON.parse(upload.tags || '[]'),
      category: upload.category || '',
      privacy_status: upload.privacy_status || 'private',
      license: upload.license || 'youtube',
      embeddable: upload.embeddable || false,
    });
    setEditModalOpen(true);
  };

  const handleEditSave = async () => {
    try {
      if (selectedUpload) {
        const updatedSchedule = { ...selectedUpload, ...editFormData };
        await editSchedule(selectedUpload.id, updatedSchedule);
        setUploads((prev) =>
          prev.map((u) => (u.id === selectedUpload.id ? { ...u, ...updatedSchedule } : u))
        );
      }
    } catch (err) {
      toastHelper.newMessage('error', err.title || 'Error', err.message || 'Edit failed');
    } finally {
      setEditModalOpen(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <div className="upload-management-container">
        <Box className="upload-management-filters" sx={{ mb: 2 }}>
          <MobileDateTimePicker
            label="Before Date"
            value={beforeDate ? dayjs(beforeDate) : null}
            onAccept={(newValue) => {
              if (newValue?.isValid()) {
                setBeforeDate(newValue.toISOString());
                setCurrentPage(1);
              }
            }}
            minutesStep={60}
            slotProps={{
              textField: {
                margin: 'normal',
                sx: { width: 250, mr: 2 },
              },
            }}
          />

          <FormControl>
            <FormLabel>Status</FormLabel>
            <RadioGroup
              row
              value={executedFilter}
              onChange={(e) => setExecutedFilter(e.target.value)}
            >
              <FormControlLabel value="all" control={<Radio />} label="All" />
              <FormControlLabel value="false" control={<Radio />} label="Scheduled" />
              <FormControlLabel value="true" control={<Radio />} label="Archived" />
            </RadioGroup>
          </FormControl>
        </Box>

        {loading ? (
          <div className="upload-management-loading">
            <CircularProgress />
          </div>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <Fade in timeout={500}>
            <div>
              <UploadTable uploads={uploads} onEdit={handleEditClick} onDelete={handleDeleteClick} />
              <PaginationControl
                totalPages={totalPages}
                currentPage={currentPage}
                onPageChange={handlePageChange}
              />
            </div>
          </Fade>
        )}

        <DeleteModal
          open={deleteModalOpen}
          onClose={() => setDeleteModalOpen(false)}
          onConfirm={handleDeleteConfirm}
          selectedUpload={selectedUpload}
        />

        <EditModal
          open={editModalOpen}
          onClose={() => setEditModalOpen(false)}
          onSave={handleEditSave}
          editFormData={editFormData}
          setEditFormData={setEditFormData}
        />
      </div>
    </LocalizationProvider>
  );
}

export default UploadManagement;
