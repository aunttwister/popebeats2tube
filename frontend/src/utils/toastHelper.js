import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const newMessage = (type, title, message) => {
    const content = (
        <div style={{ textAlign: 'left' }}>
            <h4 style={{ marginBottom: '5px' }}>{title}</h4>
            <p style={{ margin: 0 }}>{message}</p>
        </div>
    );

    if (type === 'success') {
        toast.success(content);
    } else if (type === 'error') {
        toast.error(content);
    } else {
        console.warn('Unsupported toast type:', type);
    }
};

export const toastHelper = {
    newMessage,
};
