# Extending NeoDash for Customized BKGraph Website
This README provides step-by-step instructions on how to set up your development environment to extend NeoDash for our specific needs, focusing on creating a more customized experience for querying earnings call transcripts through a knowledge graph.

> Reference: https://neo4j.com/labs/neodash/2.4/developer-guide/build-and-run/ 

## Prerequisites
Before you begin, ensure you have the following installed:

1. Yarn https://yarnpkg.com/en/docs/install 
2. Node.js https://nodejs.org/en/download 

## Getting Started
The NeoDash repository was already cloned into the `user-interface` folder.

### 1. Navigate to Project Directory
Change to the directory where you cloned the NeoDash repository:

```bash
cd neodash
```

### 2. Enable Corepack
Corepack is a Node.js tool intended to manage package managers. This command enables Corepack, preparing it to manage Yarn without needing a separate Yarn installation.
```bash
corepack enable
```

### 3. Install Dependencies
Installs all the dependencies listed in the project's package.json file using Yarn:
```bash
yarn install
```

### 4. Start Development Server
To start the development server for NeoDash, allowing you to run the application locally for development and testing purposes:
```bash
yarn run dev
```
Once the server is running, you can view the application at http://localhost:3000.

### 5. Customize NeoDash For The BKGraph Website
To customize the website, you'll find numerous files available for modification. Explore the NeoDash directories and files to identify which ones correspond to the page you're looking to edit.

