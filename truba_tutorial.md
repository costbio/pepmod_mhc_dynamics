# GROMACS on TRUBA - Lab Tutorial

This tutorial covers installing and running GROMACS with GPU acceleration on TRUBA's HPC cluster.

## Prerequisites

- Active TRUBA account with allocation
- Basic Linux/bash familiarity
- SSH access to TRUBA

## 1. Local GROMACS Installation

### Load Required Modules

TRUBA provides the necessary software as modules:

```bash
module load comp/gcc/12.3.0
module load lib/cuda/12.6
module load comp/cmake/3.31.1
```

Download and Extract GROMACS
```bash
wget https://ftp.gromacs.org/gromacs/gromacs-2025.4.tar.gz
```

Now, let's install

```bash
tar xfz gromacs-2025.4.tar.gz
cd gromacs-2025.4
Build and Install
mkdir build
cd build
cmake .. -DGMX_BUILD_OWN_FFTW=ON \
         -DREGRESSIONTEST_DOWNLOAD=ON \
         -DGMX_GPU=CUDA \
         -DCMAKE_INSTALL_PREFIX=/arf/home/your_username/gromacs

make
make check
make install
```

Note: Replace your_username with your actual TRUBA username.

Verify Installation

```bash
source /arf/home/your_username/gromacs/bin/GMXRC

gmx --version
```

You should see GPU support enabled in the output.

## 2. Environment Setup Script

Create an env.sh file with the following content:

```bash
#!/bin/bash
# Load required modules
module load comp/gcc/12.3.0
module load lib/cuda/12.6
module load comp/cmake/3.31.1

# Source GROMACS environment
source /arf/home/your_username/gromacs/bin/GMXRC

echo "GROMACS environment loaded!"
```

Usage: Source this script in every session and SLURM job:
```bash
source env.sh
```
## 3. TRUBA Node Specifications

Barbun-CUDA Nodes

CPU Cores: 40 per node
GPUs: 2x NVIDIA per node
Memory: Check with sinfo -Nel for current specs

Partition: debug (for testing)

Check Available Resources
```bash
sinfo -p debug -C barbun-cuda
squeue -p debug  # See current queue
```
## 4. Interactive Debug Session

Start an interactive session for testing:
```bash
srun -p debug \
     -C barbun-cuda \
     -A your_account \
     -N 1 \
     --ntasks=40 \
     --cpus-per-task=1 \
     --gres=gpu:2 \
     --time=00:30:00 \
     --pty bash
```
Verify GPU Access
```bash
nvidia-smi
```
Should display both GPUs.

Load Environment
```bash
source env.sh
```
Test Run
```bash
gmx mdrun -deffnm nvt \
          -v \
          -ntmpi 4 \
          -ntomp 10 \
          -nb gpu \
          -bonded gpu \
          -pme gpu \
          -npme 1 \
          -pin on \
          -nsteps 10000
```
Key flags:
-ntmpi: Number of MPI ranks (thread-MPI)
-ntomp: OpenMP threads per rank
-nb gpu: Nonbonded calculations on GPU
-bonded gpu: Bonded calculations on GPU
-pme gpu: PME electrostatics on GPU
-npme 1: Separate PME rank

## 5. Performance Optimization

For 40 cores with 2 GPUs, try different -ntmpi × -ntomp combinations (must equal 40):
### Recommended starting points:
```bash
gmx mdrun -deffnm nvt -v -ntmpi 2 -ntomp 20 -nb gpu -bonded gpu -pme gpu -npme 1 -pin on -nsteps 10000  # 1 rank per GPU
gmx mdrun -deffnm nvt -v -ntmpi 4 -ntomp 10 -nb gpu -bonded gpu -pme gpu -npme 1 -pin on -nsteps 10000
gmx mdrun -deffnm nvt -v -ntmpi 5 -ntomp 8  -nb gpu -bonded gpu -pme gpu -npme 1 -pin on -nsteps 10000
gmx mdrun -deffnm nvt -v -ntmpi 8 -ntomp 5  -nb gpu -bonded gpu -pme gpu -npme 1 -pin on -nsteps 10000
gmx mdrun -deffnm nvt -v -ntmpi 10 -ntomp 4 -nb gpu -bonded gpu -pme gpu -npme 1 -pin on -nsteps 10000
```
Compare the ns/day output to find optimal performance for your system.

Inspect Logs
```bash
less md.log  # Detailed performance metrics
```
## 6. SLURM Batch Jobs

Create a SLURM submission script run_md.sh:
```bash
#!/bin/bash
#SBATCH -p debug                    # Partition (debug/mid/long)
#SBATCH -C barbun-cuda              # Node constraint
#SBATCH -A your_account             # Your allocation code
#SBATCH -J protein_md               # Job name
#SBATCH -N 1                        # Number of nodes
#SBATCH --ntasks=40                 # Total tasks
#SBATCH --cpus-per-task=1           # CPUs per task
#SBATCH --gres=gpu:2                # GPUs requested
#SBATCH --time=03:00:00             # Time limit (HH:MM:SS)
```
### Print node info
```bash
echo "SLURM_NODELIST: $SLURM_NODELIST"
echo "NUMBER OF CORES: $SLURM_NTASKS"
echo "NUMBER OF CPUs: $SLURM_NPROCS"
```
### Load environment
```bash
source /arf/home/your_username/env.sh
```
### Run simulation
```bash
gmx mdrun -s md.tpr \
          -nsteps 500000 \
          -v \
          -ntmpi 2 \
          -ntomp 20 \
          -nb gpu \
          -bonded gpu \
          -pme gpu \
          -npme 1 \
          -pin on

exit
```
Submit Job
```bash
sbatch run_md.sh
```
Monitor Jobs
```bash
squeue -u your_username              # Check status

squeue -j <job_id>                   # Specific job details

scancel <job_id>                     # Cancel job

sacct -j <job_id> --format=JobID,JobName,Elapsed,State  # Job history
```
## 7. Tips and Common Issues

GPU not detected: Ensure -C barbun-cuda or any gpu node constraint is set
Slow performance: Try different -ntmpi/-ntomp combinations
Module errors: Reload modules after reconnecting to TRUBA
Permission denied: Check file paths and ownership

## Additional Resources

GROMACS Manual: https://manual.gromacs.org/

TRUBA Documentation: https://docs.truba.gov.tr/
