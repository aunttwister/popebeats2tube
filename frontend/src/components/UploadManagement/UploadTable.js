import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';

function UploadTable({ uploads, onEdit, onDelete }) {
  return (
    <div className="upload-management-table-container">
      <Table className="upload-management-table">
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
          {uploads.map((upload) => (
            <TableRow key={upload.id}>
              <TableCell data-label="Title">{upload.video_title}</TableCell>
              <TableCell data-label="Upload Date">
                {new Date(upload.upload_date).toLocaleDateString()}
              </TableCell>
              <TableCell data-label="Status">
                {upload.executed ? 'Archived' : 'Scheduled'}
              </TableCell>
              <TableCell data-label="Image Name">{upload.img_name || 'N/A'}</TableCell>
              <TableCell data-label="Audio Name">{upload.audio_name || 'N/A'}</TableCell>
              <TableCell data-label="Actions">
                <div className="upload-management-buttons">
                  {!upload.executed && (
                    <>
                      <Button
                        variant="outlined"
                        sx={{ marginRight: 1 }}
                        className="upload-management-button"
                        onClick={() => onEdit(upload)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        className="upload-management-button"
                        onClick={() => onDelete(upload)}
                      >
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
    </div>
  );
}

export default UploadTable;
