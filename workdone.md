# Frontend Development Work Done

This document outlines the work done on the frontend of the SmartQuery application.

## Project Structure

The frontend is a Next.js application with a well-organized structure:

- **`src/app`**: Contains the main pages of the application, including the landing page (`/`), login page (`/login`), and dashboard (`/dashboard`).
- **`src/components`**: Contains reusable components, such as authentication components, layout components, and charts.
- **`src/lib`**: Contains the core logic of the application, including the API client, authentication utilities, and type definitions.
- **`public`**: Contains static assets, such as images and icons.

## Authentication

- **Google OAuth**: The application uses Google OAuth for authentication. The login page redirects the user to Google for authentication, and the callback is handled by the frontend.
- **JWT Tokens**: The frontend uses JSON Web Tokens (JWT) for authentication. The access token is stored in local storage and sent with each request to the backend.
- **Token Refresh**: The API client automatically refreshes the access token when it expires.
- **Protected Routes**: The dashboard page is a protected route that can only be accessed by authenticated users.

## API Client

- **Axios**: The frontend uses Axios for making HTTP requests to the backend.
- **Interceptors**: The API client uses interceptors to add the authentication token to each request and to handle token refresh.
- **Retry Logic**: The API client uses a retry mechanism with exponential backoff to handle network errors.
- **Type Safety**: The API client is type-safe, with types defined for all API endpoints.

## State Management

- **Zustand**: The frontend uses Zustand for state management.
- **Stores**: The application has separate stores for authentication, projects, chat, UI, and notifications.

## UI

- **Tailwind CSS**: The frontend uses Tailwind CSS for styling.
- **Heroicons**: The application uses Heroicons for icons.
- **Recharts**: The application uses Recharts for charts.
- **Responsive Design**: The application is responsive and works well on all screen sizes.

## Features

- **Landing Page**: A beautiful landing page that showcases the features of the application.
- **Login Page**: A simple login page with Google OAuth integration.
- **Dashboard**: A protected dashboard that displays user information and provides access to the application's features.
- **File Upload**: Users can upload CSV files to the application.
- **Chat**: Users can chat with the application to analyze their data.
- **Data Visualization**: The application can generate charts to visualize data.