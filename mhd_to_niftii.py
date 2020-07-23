__author__ = 'Brian M Anderson'
# Created on 11/5/2019

import SimpleITK as sitk
import os, pickle


def load_obj(path):
    if path[-4:] != '.pkl':
        path += '.pkl'
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    else:
        output = {}
        return output


def save_obj(obj, path):
    if path[-4:] != '.pkl':
        path += '.pkl'
    with open(path, 'wb') as f:
        pickle.dump(obj, f, pickle.DEFAULT_PROTOCOL)
    return None


def main(mhd_path=None, nifti_path=None):
    if not os.path.exists(nifti_path):
        os.makedirs(nifti_path)
    for patient_path, directory, files in os.walk(mhd_path):
        if 'Image.mhd' not in files:
            continue
        image_handle = sitk.ReadImage(os.path.join(patient_path, 'Image.mhd'))
        MRN, case_id, exam = patient_path.split('\\')[-3:]
        image_path = os.path.join(nifti_path, '{}_{}_{}_Image.nii.gz'.format(MRN, case_id, exam))
        sitk.WriteImage(image_handle, image_path)
        files = [i for i in files if i.endswith('.mhd') and not i.startswith('Image')]
        for file in files:
            handle = sitk.ReadImage(os.path.join(patient_path, file))
            annotation = sitk.GetArrayFromImage(handle)
            annotation[annotation < 255/2] = 0
            annotation[annotation > 0] = 1
            out_handle = sitk.GetImageFromArray(annotation.astype('int8'))
            out_handle.SetSpacing(image_handle.GetSpacing())
            out_handle.SetOrigin(image_handle.GetOrigin())
            out_handle.SetDirection(image_handle.GetDirection())
            annotation_path = os.path.join(nifti_path, '{}_{}_{}_{}'.format(MRN, case_id, exam, file.replace('.mhd', '.nii.gz')))
            sitk.WriteImage(out_handle > 0, annotation_path)


if __name__ == '__main__':
    mhd_path = None
    nifti_path = None
    main(mhd_path, nifti_path)