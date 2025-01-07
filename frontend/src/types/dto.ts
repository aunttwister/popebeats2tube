  export interface TuneDTO {
    id: bigint; // or number
    date_created: string; // ISO 8601 format
    upload_date: string | null; // ISO 8601 format or null
    executed: boolean;
    video_title: string;
    image: string | null; // Base64 binary string that represents a file
    audio: string | null; // Base64 binary string that represents a file
  }
  