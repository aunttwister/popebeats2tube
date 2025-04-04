import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Button,
  TableContainer,
  Paper,
} from '@mui/material';

function UploadTable({ uploads, onEdit, onDelete }) {
  return (
    <TableContainer
      component={Paper}
      className="upload-management-table-container"
    >
      <Table className="upload-management-table" size="medium">
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Upload Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Image Name</TableCell>
            <TableCell>Audio Name</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {uploads.length > 0 ? (
            uploads.map((upload) => (
              <TableRow key={upload.id}>
                <TableCell data-label="Title">{upload.video_title}</TableCell>
                <TableCell data-label="Upload Date">
                  {new Date(upload.upload_date).toLocaleString()}
                </TableCell>
                <TableCell data-label="Status">
                  {upload.executed ? 'Archived' : 'Scheduled'}
                </TableCell>
                <TableCell data-label="Image Name">{upload.img_name || 'N/A'}</TableCell>
                <TableCell data-label="Audio Name">{upload.audio_name || 'N/A'}</TableCell>
                <TableCell data-label="Actions">
                  {upload.executed ? (
                    '—'
                  ) : (
                    <div className="upload-management-buttons">
                      <Button
                        variant="outlined"
                        size="small"
                        className="upload-management-button"
                        onClick={() => onEdit(upload)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        className="upload-management-button"
                        onClick={() => onDelete(upload)}
                      >
                        Delete
                      </Button>
                    </div>
                  )}
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={6} align="center">
                No uploads found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default UploadTable;
