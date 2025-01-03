import React, { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableRow, Button, CircularProgress, Typography, Pagination } from '@mui/material';
import { getSchedules } from '../../services/scheduleService.ts'; // Adjust path as per your folder structure
import './UploadManagement.css'; // Import the CSS file

function UploadManagement() {
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchSchedules = async (page) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getSchedules(page, 10); // Pass page and limit
      console.log('API response:', response);
      setUploads(response.data.data || []); // Ensure uploads is always an array
      setTotalPages(response.data.total_pages || 1); // Ensure totalPages is valid
    } catch (err) {
      console.error("Error fetching schedules:", err);
      setError('Failed to load schedules.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules(currentPage); // Fetch schedules for the current page
  }, [currentPage]);

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
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
      <Table className="upload-management-table">
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {uploads.map((upload) => (
            <TableRow key={upload.id}>
              <TableCell>{upload.video_title}</TableCell>
              <TableCell>{new Date(upload.upload_date).toLocaleDateString()}</TableCell>
              <TableCell>{upload.executed ? 'Archived' : 'Scheduled'}</TableCell>
              <TableCell>
                <div className="upload-management-buttons">
                  {!upload.executed && (
                    <>
                      <Button variant="outlined" sx={{ marginRight: 1 }} className="upload-management-button">
                        Edit
                      </Button>
                      <Button variant="outlined" color="error" className="upload-management-button">
                        Delete
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="upload-management-pagination">
        <Pagination
          count={totalPages}
          page={currentPage}
          onChange={handlePageChange}
          color="primary"
        />
      </div>
    </div>
  );
}

export default UploadManagement;
