import os
from time import sleep
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

    
    def batch(self, cmd, **kwargs):
        """
        Submit to the batch queue in non-interactive mode

        Parameters:
            cmd (str): The path to the run script that should be submitted
            kwargs of slurm arguments to pass to sbatch. The keywords will be used as
                the argument, the value as its value. If the value is False or None,
                the command is assumed to be a binary flag.
        Returns:
            job id of the new job (int)
        """
       
        out, err = self._submit('sbatch', cmd, **kwargs)
        if err:
            raise Exception('SLURM ERROR: ' + err)
        out = out.split()
        if 'error' in out:
            return 0
        try:
            job_id = int(out[-1])
        except Exception as e:
            raise e
        return job_id

    def run(self, cmd, **kwargs):
        """
        Submit to slurm controller in interactive mode

        NOTE: THIS IS A BLOCKING CALL. Control will not return until the command completes

        Parameters:
            cmd (str): the command to run
        Returns:
            the output of the job (str)
        """
        out, err = self._submit('srun', cmd, **kwargs)
        if 'error' in out:
            return False, err
        else:
            return True, out

    def _submit(self, subtype, cmd, **kwargs):

        argstring = ''
        for arg in kwargs.items():
            print arg
            argstring += ' ' + ' '.join(arg)

        cmd = [subtype, cmd, argstring] if argstring else [subtype, cmd]
        proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        print out, err
        return out, err
     
    def showjob(self, jobid):
        """
        A wrapper around scontrol show job

        Parameters:
            jobid (str): the job id to get information about
        Returns:
            A dictionary of information provided by slurm about the job
        """
        if not isinstance(jobid, str):
            jobid = str(jobid)
        tries = 0
        while tries != 10:
            proc = Popen(['scontrol', 'show', 'job', jobid], shell=False, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()
            if 'Transport endpoint is not connected' in err:
                tries += 1
                sleep(tries)
            else:
                break
        if tries == 10:
            raise Exception('SLURM ERROR: Transport endpoint is not connected')
        if 'Invalid job id specified' in err:
            raise Exception('SLURM ERROR: ' + err)
        jobinfo = {}
        for item in out.split('\n'):
            for j in item.split(' '):
                index = j.find('=')
                jobinfo[j[:index]] = j[index + 1:]
        return jobinfo

    def shownode(self, nodeid):
        """
        A wrapper around scontrol show node

        Parameters:
            jobid (str): the node id to get information about
        Returns:
            A dictionary of information provided by slurm about the node
        """
        tries = 0
        while tries != 10:
            proc = Popen(['scontrol', 'show', 'node', nodeid], shell=False, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()
            if 'Transport endpoint is not connected' in err:
                tries += 1
                sleep(tries)
            else:
                break
        if tries == 10:
            raise Exception('SLURM ERROR: Transport endpoint is not connected')
        if 'Invalid job id specified' in err:
            raise Exception('SLURM ERROR: ' + err)
        nodeinfo = {}
        for item in out.split('\n'):
            for j in item.split(' '):
                index = j.find('=')
                if index <= 0:
                    continue
                nodeinfo[j[:index]] = j[index + 1:]
        return nodeinfo

    def queue(self):
        """
        Get job queue status

        Returns: list of jobs in the queue
        """
        tries = 0
        while tries != 10:
            proc = Popen(['squeue'], shell=False, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()
            if 'Transport endpoint is not connected' in err:
                tries += 1
                sleep(tries)
            else:
                break
        if tries == 10:
            raise Exception('SLURM ERROR: Transport endpoint is not connected')

        queueinfo = []
        for item in out.split('\n')[1:]:
            if not item:
                break
            line = [x for x in item.split(' ') if x]
            queueinfo.append({
                'JOBID': line[0],
                'PARTITIION': line[1],
                'NAME': line[2],
                'USER': line[3],
                'STATE': line[4],
                'TIME': line[5],
                'NODES': line[6],
                'NODELIST(REASON)': line[7]
            })
        return queueinfo

    def cancel(self, jobid):
        """
        Cancel a job by id
        
        Parameters:
            jobid (str): The id of the job to cancel
        Returns:
            True of the job was canceled, False otherwise
        """
        if not isinstance(jobid, str):
            jobid = str(jobid)
        tries = 0
        while tries != 10:
            proc = Popen(['scancel', jobid], shell=False, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()
            if 'Transport endpoint is not connected' in err:
                tries += 1
                sleep(tries)
            else:
                break
        if tries == 10:
            raise Exception('SLURM ERROR: Transport endpoint is not connected')

        jobinfo = self.showjob(jobid)
        if jobinfo['JobState'] == 'CANCELLED':
            return True
        else:
            return False
