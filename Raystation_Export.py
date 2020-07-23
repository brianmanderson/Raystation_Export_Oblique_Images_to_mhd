__author__ = 'Brian M Anderson'
# Created on 11/4/2019

from connect import *
import os


def pull_wanted_items(line):
    broken_up = line.split(' ')
    wanted_items = []
    equal_found = False
    for item in broken_up:
        if item.find('=') != -1:
            equal_found = True
        elif equal_found:
            wanted_items.append(item)
    return wanted_items

def create_exam_specified_grid_settings(exam_path):
    output_dict = {'Corner': {}, 'VoxelSize': {}, 'NumberOfVoxels': 0}
    fid = open(exam_path)
    for line in fid:
        line = line.strip('\n')
        if line.find('Offset') != -1:
            wanted_items = pull_wanted_items(line)
            print(wanted_items)
            output_dict['Corner'] = {'x':float(wanted_items[0])/10,'y':float(wanted_items[1])/10,'z':float(wanted_items[2])/10}
            print(output_dict['Corner'])
        elif line.find('ElementSpacing') != -1:
            wanted_items = pull_wanted_items(line)
            output_dict['VoxelSize'] = {'x':float(wanted_items[0])/10,'y':float(wanted_items[1])/10,'z':float(wanted_items[2])/10}
        elif line.find('DimSize') != -1:
            wanted_items = pull_wanted_items(line)
            output_dict['NumberOfVoxels'] = {'x': wanted_items[0], 'y': wanted_items[1], 'z': wanted_items[2]}
    return output_dict


class Change_Patient(object):
    def __init__(self):
        self.patient_db = get_current("PatientDB")
    def ChangePatient(self,MRN):
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=False)
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=True)
        for info in info_all:
            if info['PatientID'] == MRN:
                break
        patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
        return patient


def export_image(path,case,exam):
    case.Examinations[exam.Name].ExportExaminationAsMetaImage(MetaFileName=os.path.join(path,'Image.mhd'))
    return None


def main(base_export_path, MRNs=None):
    assert type(MRNs) is list, 'Pass a list of MRNs to run'
    if not os.path.exists(base_export_path):
        os.makedirs(base_export_path)
    change_patient_class = Change_Patient()
    for MRN in MRNs:
        patient = change_patient_class.ChangePatient(MRN)
        for case in patient.Cases:
            exam_grid_settings = {}
            rois_in_case = []
            for roi in case.PatientModel.RegionsOfInterest:
                rois_in_case.append(roi.Name)
            for roi in rois_in_case:
                for exam in case.Examinations:
                    if exam.Name.find('MR') == -1:
                        continue
                    out_path = os.path.join(base_export_path, MRN, case.CaseName, exam.Name)
                    if os.path.exists(os.path.join(out_path,roi+'.mhd')):
                        continue
                    elif case.PatientModel.StructureSets[exam.Name].RoiGeometries[roi].HasContours():
                        if not os.path.exists(os.path.join(out_path,'Image.mhd')):
                            os.makedirs(out_path)
                            export_image(out_path,case,exam)
                        if exam.Name not in exam_grid_settings:
                            grid_settings_dict = create_exam_specified_grid_settings(os.path.join(out_path, 'Image.mhd'))
                            exam_grid_settings[exam.Name] = grid_settings_dict
                        grid_settings_dict = exam_grid_settings[exam.Name]
                        grid_settings_dict['MetaFileName'] = os.path.join(out_path,roi+'.mhd')
                        try:
                            case.PatientModel.StructureSets[exam.Name].RoiGeometries[roi].ExportRoiGeometryAsMetaImageWithSpecifiedGridSettings(**grid_settings_dict)
                        except:
                            print('failed here')
                            continue


if __name__ == '__main__':
    MRNs = None
    main(MRNs)
