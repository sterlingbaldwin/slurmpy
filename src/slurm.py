import os
from subprocess import Popen, PIPE


class Slurm(object):
    """A python interface for slurm using subprocesses

    """
    def __init__(self):
        """
        Check if the system has Slurm installed
        """
        if not any(os.access(os.path.join(path, 'sinfo'), os.X_OK) for path in os.environ["PATH"].split(os.pathsep)):
            raise Exception('Unable to find slurm, is it installed on this sytem?')

    
    def sbatch(self, _path, **kwargs):
        """
        Submit to the batch queue in non-interactive mode
        
        Parameters:
            path (str): The path to the run script that should be submitted
            kwargs of slurm arguments to pass to sbatch. The keywords will be used as 
                the argument, the value as its value. If the value is False or None,
                the command is assumed to be a binary flag.
        
        returns:
            job id of the new job (int)
        """
        argstring = ''
        for arg in kwargs.items():
            argstring += ' ' + ' '.join(arg)
    
        cmd = ['sbatch', _path, argstring]
        p = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if err:
            raise Exception('SLURM ERROR' + err)
        out = out.split()
        job_id = 0
        for item, index in enumerate(out):
            if item = 'Job':
                job_id = out[index + 1]
                if isinstance(job_id, str):
                    job_id =  int(job_id)
                    break
        return job_id

    def srun(self, cmd, **kwargs):
        """
        Submit to slurm controller in interactive mode

        Parameters:
            cmd (str): the command to run
        
        returns:
            the output of the job (str)
        """
        pass
     
    def control(self, cmd, **kwargs):
        """
        Send commands to the slurm controller
        
        Parameters:
            cmd (str): the primary command to send
            kwargs: several subcommands are allowed here, for example
                if cmd = 'show', then kwarg could have {'subcommand': job', 'job_id': '42'} to run the command
                'scontrol show job 42'

        returns:
            """
        pass
    
    def queue(self):
        """
        Get job queue status
        
        returns: list of jobs in the queue
        """
        pass