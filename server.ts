import { createServer } from 'http';
import { parse } from 'url';
import next from 'next';
import { initializeSocket } from './lib/socket-server';

const dev = process.env.NODE_ENV !== 'production';
const hostname = process.env.HOSTNAME || 'localhost';
const port = parseInt(process.env.PORT || '3000', 10);

// Create Next.js app
const app = next({ dev, hostname, port });
const handle = app.getRequestHandler();

// Prepare the Next.js app
app.prepare().then(() => {
  // Create HTTP server
  const httpServer = createServer(async (req, res) => {
    try {
      // Parse URL
      const parsedUrl = parse(req.url || '', true);

      // Handle Socket.io requests
      if (parsedUrl.pathname?.startsWith('/api/socket.io/')) {
        // Socket.io middleware will handle this
        return;
      }

      // Handle all other requests through Next.js
      await handle(req, res, parsedUrl);
    } catch (err) {
      console.error('Error handling request:', err);
      res.statusCode = 500;
      res.end('Internal server error');
    }
  });

  // Initialize Socket.io on the HTTP server
  initializeSocket(httpServer);

  // Start server
  httpServer.listen(port, () => {
    console.log(`
      ╔════════════════════════════════════════╗
      ║  🚀 Esad Chat Server Started           ║
      ║  📍 URL: http://${hostname}:${port}     ║
      ║  🔌 WebSocket: ws://localhost:${port}  ║
      ║  🌍 Node: ${process.env.NODE_ENV || 'development'}                    ║
      ╚════════════════════════════════════════╝
    `);
  });

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    httpServer.close(() => {
      console.log('Server closed');
      process.exit(0);
    });
  });
});
