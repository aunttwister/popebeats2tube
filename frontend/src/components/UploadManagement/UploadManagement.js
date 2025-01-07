import React, { useEffect, useState } from 'react';
import { CircularProgress, Typography } from '@mui/material';
import UploadTable from './UploadTable';
import PaginationControl from './PaginationControl';
import DeleteModal from './DeleteModal';
import EditModal from './EditModal';
import { getSchedules, editSchedule, removeSchedule } from '../../services/scheduleTuneService.ts';
import dayjs from 'dayjs';
import './UploadManagement.css';
import { toastHelper } from '../../utils/toastHelper';

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

  const fetchSchedules = async (page) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getSchedules(page, 10);
      setUploads(response.data.data || []);
      setTotalPages(response.data.total_pages || 1);
      toastHelper.newMessage('success', response.title, response.message)
    } catch (err) {
      toastHelper.newMessage('error', err.title, err.message)
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules(currentPage);
  }, [currentPage]);

  const handlePageChange = (event, value) => setCurrentPage(value);

  const handleDeleteClick = (upload) => {
    setSelectedUpload(upload);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      if (selectedUpload) {
        await removeSchedule(selectedUpload.id);
        setUploads(uploads.filter((u) => u.id !== selectedUpload.id));
      }
    } catch (err) {
      toastHelper.newMessage('error', err.title, err.detail)
    } finally {
      setDeleteModalOpen(false);
    }
  };

  const handleEditClick = (upload) => {
    setSelectedUpload(upload);
    setEditFormData({
      video_title: upload.video_title || '',
      video_description: upload.video_description || '', // Ensure description is passed
      upload_date: dayjs(upload.upload_date), // Convert to dayjs object
      tags: Array.isArray(upload.tags) ? upload.tags : JSON.parse(upload.tags || '[]'), // Ensure tags is an array
      category: upload.category || '', // Pass category
      privacy_status: upload.privacy_status || 'private', // Default to 'private'
      license: upload.license || 'youtube', // Default to 'youtube'
      embeddable: upload.embeddable || false, // Default to false
    });
    setEditModalOpen(true);
  };

  const handleEditSave = async () => {
    try {
      if (selectedUpload) {
        const updatedSchedule = { ...selectedUpload, ...editFormData };
        await editSchedule(selectedUpload.id, updatedSchedule);
        setUploads(
          uploads.map((u) => (u.id === selectedUpload.id ? { ...u, ...updatedSchedule } : u))
        );
      }
    } catch (err) {
      toastHelper.newMessage('error', err.title, err.message)
    } finally {
      setEditModalOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="upload-management-loading">
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <div className="upload-management-container">
        <Typography color="error">{error}</Typography>
      </div>
    );
  }

  return (
    <div className="upload-management-container">
      <UploadTable uploads={uploads} onEdit={handleEditClick} onDelete={handleDeleteClick} />
      <PaginationControl totalPages={totalPages} currentPage={currentPage} onPageChange={handlePageChange} />
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
  );
}

export default UploadManagement;
