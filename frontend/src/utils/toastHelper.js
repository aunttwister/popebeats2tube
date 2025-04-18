import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const newMessage = (type, title, message) => {
    const content = (
        <div style={{ fontSize: '0.85rem', lineHeight: '1.2rem' }}>
            {title && <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{title}</div>}
            <div>{message}</div>
        </div>
    );

    const options = {
        position: 'bottom-right',
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: false,
        style: {
            minHeight: '40px',
            padding: '8px 12px',
            fontSize: '0.85rem',
        },
    };

    if (type === 'success') {
        toast.success(content, options);
    } else if (type === 'error') {
        toast.error(content, options);
    } else if (type === 'info') {
        toast.info(content, options);
    } else {
        console.warn('Unsupported toast type:', type);
    }
};

export const toastHelper = {
    newMessage,
};
